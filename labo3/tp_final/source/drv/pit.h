/**
 * @file pit.h
 * @brief Periodic Interrupt Timer driver for Kinetis K64 (MK64F12)
 *
 *  - 4 independent channels (PIT_CH0 … PIT_CH3)
 *  - 32-bit down-counter, bus-clock source (@ 50 MHz on FRDM K64F)
 *  - Frequency range: 25 MHz - 12 mHz
 *  - One-shot or periodic mode
 *  - Optional DMA request on timeout
 *  - Callback per channel (major interrupt)
 */

#ifndef _PIT_H_
#define _PIT_H_

#include <stdint.h>
#include <stdbool.h>

/*******************************************************************************
 * DEFINES
 ******************************************************************************/

// System Bus Clock @ 50 MHz
#ifndef SYS_BUS_CLK
#define SYS_BUS_CLK (50000000UL)
#endif

#define PIT_TICKS_FROM_US(us) ((uint32_t)((((SYS_BUS_CLK/1000000UL)*(us)) - 1)))
#define PIT_TICKS_FROM_MS(ms) ((uint32_t)((((SYS_BUS_CLK/1000UL)*(ms)) - 1)))
#define PIT_CHANNELS 4

/*******************************************************************************
 * PUBLIC TYPES
 ******************************************************************************/

/* PIT channel identifier */
typedef enum
{
    PIT_CH0 = 0,
    PIT_CH1 = 1,
    PIT_CH2 = 2,
    PIT_CH3 = 3,
} pit_ch_e;

/* Callback prototype – called from ISR when a timer expires */
typedef void (*pit_cb_t)(void *user);

/* Configuration structure – one per channel */
typedef struct
{
    pit_ch_e   ch;          // PIT_CH0 … PIT_CH3                       
    uint32_t   load_val;    // LDVAL register – ticks to count down    
    bool       periodic;    // true->periodic / false->one-shot
    bool       int_en;      // true->enable interrupt (callback)       
    bool       dma_req;     // true->assert DMA request on timeout     
    pit_cb_t   callback;    // may be NULL                               
    void      *user;        // cookie passed to callback                 
} pit_cfg_t;

/*******************************************************************************
 * PUBLIC API
 ******************************************************************************/

/**
 * @brief Global PIT initialization (clocks + NVIC)
 */
void PIT_Init(void);

/**
 * @brief Configure a PIT channel. If periodic mode enabled, it starts 
 * automatically
 * @param cfg Pointer to filled configuration structure
 * @return true on success, false on error
 */
bool PIT_Config(const pit_cfg_t *cfg);

/**
 * @brief (Re)start a channel
 * @param ch  Channel to start
 * @return true on success, false on error
 */
bool PIT_Start(pit_ch_e ch);

/**
 * @brief Stop a channel (disable timer & request)
 * @param ch  Channel to stop
 * @return true on success, false on error
 */
bool PIT_Stop(pit_ch_e ch);

/**
 * @brief Change the load value on-the-fly (periodic mode only)
 * @param ch        Channel
 * @param new_load  New LDVAL value
 * @return true on success, false on error
 */
bool PIT_SetLoad(pit_ch_e ch, uint32_t new_load);

/**
 * @brief Get remaining ticks (for debugging / sync)
 * @param ch  Channel
 * @return Current CVAL value (0 = expired)
 */
uint32_t PIT_GetCount(pit_ch_e ch);

#endif // _PIT_H_ 
