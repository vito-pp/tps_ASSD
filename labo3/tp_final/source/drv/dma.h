/**
 * @file dma.h
 * @brief DMA (eDMA/DMAMUX) driver public API and configuration types.
 */

#ifndef _DMA_H_
#define _DMA_H_

/*******************************************************************************
 * INCLUDES
 ******************************************************************************/

#include <stdint.h>
#include <stdbool.h>

/*******************************************************************************
 * DEFINES
 ******************************************************************************/

#define DMA_NUM_CH 16

/*******************************************************************************
 * PUBLIC TYPES
 ******************************************************************************/

typedef enum
{
    /* 0–9: UART0..UART3 */
    DMA_REQ_DISABLED           = 0,   // Channel disabled
    DMA_REQ_UART0_RX           = 2,
    DMA_REQ_UART0_TX           = 3,
    DMA_REQ_UART1_RX           = 4,
    DMA_REQ_UART1_TX           = 5,
    DMA_REQ_UART2_RX           = 6,
    DMA_REQ_UART2_TX           = 7,
    DMA_REQ_UART3_RX           = 8,
    DMA_REQ_UART3_TX           = 9,

    /* 10–19: UART4/5, I2S0, SPI0/1/2, I2C */
    DMA_REQ_UART4_RXTX         = 10,  // “Transmit or Receive”
    DMA_REQ_UART5_RXTX         = 11,  // “Transmit or Receive”
    DMA_REQ_I2S0_RX            = 12,
    DMA_REQ_I2S0_TX            = 13,
    DMA_REQ_SPI0_RX            = 14,
    DMA_REQ_SPI0_TX            = 15,
    DMA_REQ_SPI1_RXTX          = 16,  // “Transmit or Receive”
    DMA_REQ_SPI2_RXTX          = 17,  // “Transmit or Receive”
    DMA_REQ_I2C0               = 18,  
    DMA_REQ_I2C1_OR_I2C2       = 19,  

    /* 20–39: FTM0..FTM3 channels */
    DMA_REQ_FTM0CH0            = 20,
    DMA_REQ_FTM0CH1            = 21,
    DMA_REQ_FTM0CH2            = 22,
    DMA_REQ_FTM0CH3            = 23,
    DMA_REQ_FTM0CH4            = 24,
    DMA_REQ_FTM0CH5            = 25,
    DMA_REQ_FTM0CH6            = 26,
    DMA_REQ_FTM0CH7            = 27,
    DMA_REQ_FTM1CH0            = 28,
    DMA_REQ_FTM1CH1            = 29,
    DMA_REQ_FTM2CH0            = 30,
    DMA_REQ_FTM2CH1            = 31,
    DMA_REQ_FTM3CH0            = 32,
    DMA_REQ_FTM3CH1            = 33,
    DMA_REQ_FTM3CH2            = 34,
    DMA_REQ_FTM3CH3            = 35,
    DMA_REQ_FTM3CH4            = 36,
    DMA_REQ_FTM3CH5            = 37,
    DMA_REQ_FTM3CH6            = 38,
    DMA_REQ_FTM3CH7            = 39,

    /* 40–48: analog + timers */
    DMA_REQ_ADC0               = 40,
    DMA_REQ_ADC1               = 41,
    DMA_REQ_CMP0               = 42,
    DMA_REQ_CMP1               = 43,
    DMA_REQ_CMP2               = 44,
    DMA_REQ_DAC0               = 45,
    DMA_REQ_DAC1               = 46,
    DMA_REQ_CMT                = 47,
    DMA_REQ_PDB                = 48,

    /* 49–53: Port control (GPIO) */
    DMA_REQ_PORTA              = 49,
    DMA_REQ_PORTB              = 50,
    DMA_REQ_PORTC              = 51,
    DMA_REQ_PORTD              = 52,
    DMA_REQ_PORTE              = 53,

    /* 58–63: DMAMUX “Always enabled” (software trigger) */
    DMA_REQ_ALWAYS58           = 58,
    DMA_REQ_ALWAYS59           = 59,
    DMA_REQ_ALWAYS60           = 60,
    DMA_REQ_ALWAYS61           = 61,
    DMA_REQ_ALWAYS62           = 62,
    DMA_REQ_ALWAYS63           = 63
} dma_req_e;

typedef void (*dma_cb_t)(void *user);

typedef struct 
{
    uint8_t ch;             // DMA channel 0..15
    dma_req_e request_src;  // request source
    bool trig_mode;         // true->trigger mode, false->normal mode
    void *saddr;            // source addr
    void *daddr;            // destination addr
    uint8_t nbytes;         // 1, 2, or 4 bytes
    int16_t soff, doff;     // source and destination offset in bytes
    uint16_t major_count;   // elements per major loop
    int32_t slast;          // pointer adjust @major end (source)
    int32_t dlast;          // pointer adjust @major end (dest)
    bool int_major;         // false/true
    //bool int_half;          // false/true
    dma_cb_t on_major;      // may be NULL
    //dma_cb_t on_half;       // may be NULL
    void *user;             // user cookie for both callbacks
} dma_cfg_t;

/*******************************************************************************
 * PUBLIC API
 ******************************************************************************/

/**
 * @brief Initialize the eDMA/DMAMUX driver (once).
 *
 * Enables module clocks, configures global eDMA settings, and hooks NVIC ISRs
 * for all DMA channel IRQs used by the HAL.
 *
 * @retval 0  Success.
 * @retval <0 Error (already initialized or clock/NVIC issue).
 */
int DMA_Init(void);                     

/**
 * @brief Configure one DMA channel (TCD + DMAMUX) from a @ref dma_cfg_t.
 *
 * Programs the TCD fields (SADDR/DADDR/NBYTES/SOFF/DOFF/CITER/BITER/SLAST/
 * DLAST)
 * and the DMAMUX channel source/trigger mode.
 *
 * @param[in] cfg  Pointer to the channel configuration.
 *
 * @retval 0   Success.
 * @retval <0  Error (invalid channel, bad sizes/alignments, or null pointer).
 */
int DMA_Config(const dma_cfg_t *cfg); 

/**
 * @brief Enable request (ERQ) for a configured channel (arm it).
 *
 * @param ch  DMA channel index [0..15].
 * @retval 0   Success.
 * @retval <0  Error (invalid channel or not configured).
 */
int DMA_Start(uint8_t ch);


/**
 * @brief Disable request (ERQ) for a channel (disarm it).
 *
 * Does not clear the TCD. You can @ref DMA_Start it again later.
 *
 * @param ch  DMA channel index [0..15].
 * @retval 0   Success.
 * @retval <0  Error (invalid channel).
 */
int DMA_Stop(uint8_t ch);

#endif