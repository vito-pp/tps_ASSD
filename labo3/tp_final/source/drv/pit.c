/*======================================================================
 *  Includes
 *====================================================================*/

#include <stddef.h>
#include "MK64F12.h"
#include "pit.h"
#include "board.h"
#include "gpio.h"

/*======================================================================
 *  Static variables
 *====================================================================*/

static pit_cb_t  g_callbacks[PIT_CHANNELS] = {NULL};
static void     *g_users[PIT_CHANNELS]     = {NULL};

/*======================================================================
 *  Global Functions
 *====================================================================*/

void PIT_Init(void)
{
    /* 1. Enable clock for PIT */
    SIM->SCGC6 |= SIM_SCGC6_PIT_MASK;

    /* 2. Enable timers, freeze in debug if desired */
    PIT->MCR = PIT_MCR_FRZ_MASK;  // MDIS=0 (enable), FRZ=1 (freeze in debug)

    /* 3. Enable IRQs in NVIC */
    NVIC_EnableIRQ(PIT0_IRQn);
}

bool PIT_Config(const pit_cfg_t *cfg)
{
    if (cfg == NULL || cfg->ch >= PIT_CHANNELS || cfg->load_val == 0) 
    {
        return false;
    }

    uint8_t ch = cfg->ch;

    /* 1. Stop timer first */
    PIT->CHANNEL[ch].TCTRL = 0;

    /* 2. Set load value */
    PIT->CHANNEL[ch].LDVAL = cfg->load_val;

    /* 3. Clear interrupt flag */
    PIT->CHANNEL[ch].TFLG = PIT_TFLG_TIF_MASK;

    /* 4. Store callback */
    g_callbacks[ch] = cfg->callback;
    g_users[ch]     = cfg->user;

    /* 5. Configure TCTRL */
    uint32_t tctrl = 0;

    if (cfg->int_en) 
    {
        tctrl |= PIT_TCTRL_TIE_MASK;
    }

    if (cfg->dma_req) 
    {
        tctrl |= PIT_TCTRL_TEN_MASK;  // DMA request on timeout
    }

    PIT->CHANNEL[ch].TCTRL = tctrl;

    /* 6. Start in periodic mode if requested */
    if (cfg->periodic)
    {
        PIT_Start(cfg->ch);
    }

    return true;
}

bool PIT_Start(pit_ch_e ch)
{
    if (ch >= PIT_CHANNELS) return false;
    PIT->CHANNEL[ch].TCTRL |= PIT_TCTRL_TEN_MASK;
    return true;
}

bool PIT_Stop(pit_ch_e ch)
{
    if (ch >= PIT_CHANNELS) return false;
    PIT->CHANNEL[ch].TCTRL &= ~PIT_TCTRL_TEN_MASK;
    return true;
}

bool PIT_SetLoad(pit_ch_e ch, uint32_t new_load)
{
    if (ch >= PIT_CHANNELS || new_load == 0) return false;

    /* Only safe if timer is running in periodic mode */
    if (PIT->CHANNEL[ch].TCTRL & PIT_TCTRL_TEN_MASK) 
    {
        PIT->CHANNEL[ch].LDVAL = new_load;
    }
    return true;
}

uint32_t PIT_GetCount(pit_ch_e ch)
{
    if (ch >= PIT_CHANNELS) return true;
    return PIT->CHANNEL[ch].CVAL;
}

/*======================================================================
 *  ISR Handlers
 *====================================================================*/

static void pit_isr_handler(uint8_t ch)
{
    /* Clear flag */
    PIT->CHANNEL[ch].TFLG = PIT_TFLG_TIF_MASK;

    /* Call user callback */
    if (g_callbacks[ch]) 
    {
        g_callbacks[ch](g_users[ch]);
    }
}

void PIT0_IRQHandler(void) 
{
    gpioWrite(PIN_TP2, HIGH);
    int i;
    for (i = 0; i < PIT_CHANNELS; i++)
    {
        if (PIT->CHANNEL[i].TFLG == PIT_TFLG_TIF_MASK)
        {
            pit_isr_handler(i);
        }
    }
    gpioWrite(PIN_TP2, LOW);  
}
// no existen en el Kinetis :^(
// void PIT1_IRQHandler(void) { pit_isr_handler(1); }
// void PIT2_IRQHandler(void) { pit_isr_handler(2); }
// void PIT3_IRQHandler(void) { pit_isr_handler(3); }
