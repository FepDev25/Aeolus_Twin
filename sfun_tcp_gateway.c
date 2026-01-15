/**
 * @file sfun_tcp_gateway.c
 * @brief S-Function para comunicación TCP/IP entre Simulink y servidor externo
 *
 * Implementa un cliente TCP/IP síncrono (lock-step) compatible con Linux y Windows.
 * Protocolo de comunicación:
 *   - Entrada: 4 doubles (wm, P, V, S) desde Simulink
 *   - Salida: 2 doubles (velocidad_viento, pitch) hacia Simulink
 *
 * @author Equipo Elecaustro
 * @version 2.0
 * @date 2026-01-14
 */

#define S_FUNCTION_NAME sfun_tcp_gateway
#define S_FUNCTION_LEVEL 2

/*
 * DEPENDENCIAS ESPECÍFICAS DE PLATAFORMA
 * */

#ifndef _WIN32
    /* Plataforma Unix/Linux: usar sockets POSIX */
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <netinet/in.h>
    #include <netdb.h>
    #include <errno.h>
    #include <fcntl.h>
    
    /* Abstracción de tipos para compatibilidad con Windows */
    typedef int SOCKET;
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define closesocket(s) close(s)
    #define WSAGetLastError() errno
#else
    /* Plataforma Windows: usar Winsock2 */
    #define WIN32_LEAN_AND_MEAN
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
#endif

#include "mex.h"
#include "simstruc.h"
#include <string.h>
#include <stdio.h>

/*
 * CONFIGURACIÓN DE PARÁMETROS Y PUERTOS
 * */

/* Acceso a parámetros del bloque S-Function en Simulink */
#define IP_ADDRESS_PARAM(S) ssGetSFcnParam(S, 0)
#define PORT_PARAM(S)       ssGetSFcnParam(S, 1)

/* Dimensiones de datos de comunicación */
#define INPUT_WIDTH 4        /* Telemetría: wm, P, V, S */
#define OUTPUT_WIDTH 2       /* Control: velocidad_viento, pitch */
#define DATA_TYPE SS_DOUBLE

/* Almacenamiento persistente del descriptor de socket */
#define P_SOCKET(S) (SOCKET*)ssGetPWork(S)

/*
 * FUNCIÓN: mdlInitializeSizes
 * PROPÓSITO: Configurar puertos de entrada/salida y parámetros
 * LLAMADA: Una vez al inicio de la simulación
 * */
static void mdlInitializeSizes(SimStruct *S)
{
    /* Validar número de parámetros (IP, Puerto) */
    ssSetNumSFcnParams(S, 2);
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
        ssSetErrorStatus(S, "Número incorrecto de parámetros. Se esperan 2 (IP, Puerto).");
        return;
    }
    
    /* Configurar puerto de entrada (telemetría desde Simulink) */
    if (!ssSetNumInputPorts(S, 1)) return;
    ssSetInputPortWidth(S, 0, INPUT_WIDTH);
    ssSetInputPortDataType(S, 0, DATA_TYPE);
    ssSetInputPortRequiredContiguous(S, 0, true);
    ssSetInputPortDirectFeedThrough(S, 0, 1);

    /* Configurar puerto de salida (comandos de control hacia Simulink) */
    if (!ssSetNumOutputPorts(S, 1)) return;
    ssSetOutputPortWidth(S, 0, OUTPUT_WIDTH);
    ssSetOutputPortDataType(S, 0, DATA_TYPE);

    ssSetNumSampleTimes(S, 1);
    
    /* Reservar espacio para almacenar el descriptor de socket */
    ssSetNumPWork(S, 1);
    ssSetSimStateCompliance(S, USE_DEFAULT_SIM_STATE);
}

/*
 * FUNCIÓN: mdlInitializeSampleTimes
 * PROPÓSITO: Definir el tiempo de muestreo
 * */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, INHERITED_SAMPLE_TIME);
    ssSetOffsetTime(S, 0, 0.0);
}

/*
 * FUNCIÓN: mdlStart
 * PROPÓSITO: Inicializar conexión TCP/IP al servidor
 * LLAMADA: Una vez al inicio de la simulación
 * */
#define MDL_START
static void mdlStart(SimStruct *S)
{
    /* Extraer parámetros de configuración */
    int_T port = (int_T) *mxGetPr(PORT_PARAM(S));
    char ipAddr[20];
    mxGetString(IP_ADDRESS_PARAM(S), ipAddr, sizeof(ipAddr));
    
#ifdef _WIN32
    /* Windows: inicializar subsistema Winsock */
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        ssSetErrorStatus(S, "Fallo al inicializar Winsock (WSAStartup)");
        return;
    }
#endif

    SOCKET sock_fd;
    struct sockaddr_in serverAddr;

    /* Crear socket TCP */
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (sock_fd == INVALID_SOCKET) {
        char err_msg[100];
        snprintf(err_msg, sizeof(err_msg), "Fallo al crear el socket. Error: %d", WSAGetLastError());
        ssSetErrorStatus(S, err_msg);
#ifdef _WIN32
        WSACleanup();
#endif
        return;
    }

    /* Configurar dirección del servidor */
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    
    /* Convertir dirección IP de texto a formato binario */
    if (inet_pton(AF_INET, ipAddr, &serverAddr.sin_addr) <= 0) {
        ssSetErrorStatus(S, "Dirección IP inválida o no soportada");
        closesocket(sock_fd);
#ifdef _WIN32
        WSACleanup();
#endif
        return;
    }

    /* Establecer conexión con el servidor */
    if (connect(sock_fd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        char err_msg[150];
        snprintf(err_msg, sizeof(err_msg), "Fallo al conectar. Error: %d. ¿Está el servidor en %s:%d?", WSAGetLastError(), ipAddr, port);
        ssSetErrorStatus(S, err_msg);
        closesocket(sock_fd);
#ifdef _WIN32
        WSACleanup();
#endif
        return;
    }
    
    /* Guardar descriptor de socket para uso posterior */
    *P_SOCKET(S) = sock_fd;
    ssPrintf("S-Function: Conectado exitosamente a %s:%d\n", ipAddr, port);
}

/*
 * FUNCIÓN: mdlOutputs
 * PROPÓSITO: Ejecutar comunicación síncrona bidireccional
 * LLAMADA: En cada paso de tiempo de la simulación
 * PROTOCOLO: Lock-step (enviar telemetría → recibir comandos)
 * */
static void mdlOutputs(SimStruct *S, int_T tid)
{
    SOCKET sock_fd = *P_SOCKET(S);
    const real_T *in_data = ssGetInputPortRealSignal(S, 0);
    real_T *out_data = ssGetOutputPortRealSignal(S, 0);

    ssize_t send_result, recv_result;
    const size_t in_bytes = INPUT_WIDTH * sizeof(double);
    const size_t out_bytes = OUTPUT_WIDTH * sizeof(double);

    /* Fase 1: Enviar telemetría a servidor */
    send_result = send(sock_fd, (const void*)in_data, in_bytes, 0);
    
    if (send_result == SOCKET_ERROR) {
        char err_msg[100];
        snprintf(err_msg, sizeof(err_msg), "Fallo al enviar datos. Error: %d", WSAGetLastError());
        ssSetErrorStatus(S, err_msg);
        return;
    }
    if (send_result != (ssize_t)in_bytes) {
        ssSetErrorStatus(S, "Error: No se enviaron todos los bytes.");
        return;
    }

    /* Fase 2: Recibir comandos de control (bloqueante) */
    recv_result = recv(sock_fd, (void*)out_data, out_bytes, MSG_WAITALL);

    /* Verificar resultado de recepción */
    if (recv_result == 0) {
        ssSetErrorStatus(S, "Conexión cerrada por el servidor Python");
    } else if (recv_result == SOCKET_ERROR) {
        char err_msg[100];
        snprintf(err_msg, sizeof(err_msg), "Fallo al recibir datos. Error: %d", WSAGetLastError());
        ssSetErrorStatus(S, err_msg);
    } else if (recv_result != (ssize_t)out_bytes) {
        char err_msg[100];
        snprintf(err_msg, sizeof(err_msg), "Error: Se esperaban %zu bytes, se recibieron %zd", out_bytes, recv_result);
        ssSetErrorStatus(S, err_msg);
    }
}

/*
 * FUNCIÓN: mdlTerminate
 * PROPÓSITO: Liberar recursos y cerrar conexión
 * LLAMADA: Una vez al final de la simulación
 * */
static void mdlTerminate(SimStruct *S)
{
    SOCKET sock_fd = *P_SOCKET(S);
    
    if (sock_fd != INVALID_SOCKET) {
        ssPrintf("S-Function: Cerrando conexión.\n");
        closesocket(sock_fd);
    }
    
#ifdef _WIN32
    /* Windows: liberar recursos de Winsock */
    WSACleanup();
#endif
}

/*
 * CÓDIGO BOILERPLATE DE SIMULINK
 * */
#ifdef MATLAB_MEX_FILE
#include "simulink.c"
#else
#include "cg_sfun.h"
#endif