#include "dma.h"
#include "MK64F12.h"
#include "hardware.h"
#include "board.h"
#include "gpio.h"

static bool initialized = false;

typedef struct 
{
    dma_cb_t on_major_cb;
    void *user_param;
    bool active;
} dma_state_t;

static dma_state_t dma_ch_states[DMA_NUM_CH];

static int size2code(uint8_t bytes);
static void DMA_IRQHandler(uint8_t ch);

int DMA_Init(void)
{
    if (initialized) return -1;

    // Enable clocks
    SIM->SCGC7 |= SIM_SCGC7_DMA_MASK;
    SIM->SCGC6 |= SIM_SCGC6_DMAMUX_MASK;

    // Configure DMA CR (optional settings for simplicity)
    DMA0->CR = DMA_CR_ERCA_MASK |  // Round-robin arbitration
               DMA_CR_HOE_MASK |   // Halt on error
               DMA_CR_EMLM_MASK;   // Enable minor loop mapping

    // Clear errors
    DMA0->ERR = 0xFFFFFFFFU;

    initialized = true;
    return 0;
}

int DMA_Config(const dma_cfg_t *cfg)
{
    // Validate
    int ch = cfg->ch;
    if (ch >= DMA_NUM_CH)
    {
        return -1;
    }
    // Disarm and clear pending IRQs before configuring
    DMA0->CERQ = DMA_CERQ_CERQ(cfg->ch);
	NVIC_ClearPendingIRQ(DMA0_IRQn + ch);
	if (cfg->int_major) 
    {
        NVIC_EnableIRQ(DMA0_IRQn + ch);
    }
    else
    {
        NVIC_DisableIRQ(DMA0_IRQn + ch);
    }

    // Remember config
    dma_ch_states[ch].on_major_cb = cfg->on_major;
    dma_ch_states[ch].user_param = cfg->user;

    // Enable the eDMA channel and set the DMA request source
    DMAMUX->CHCFG[ch] = 0;
	DMAMUX->CHCFG[ch] |= DMAMUX_CHCFG_ENBL_MASK 
                        |DMAMUX_CHCFG_SOURCE((uint8_t)cfg->request_src);
    if (cfg->trig_mode) // If trigger mode enabled
    {
        DMAMUX->CHCFG[ch] |= DMAMUX_CHCFG_TRIG_MASK;
    }

    // -------------- TCD setup ----------------------
    DMA0->TCD[ch].SADDR= (uint32_t)(cfg->saddr);
	DMA0->TCD[ch].DADDR = (uint32_t)(cfg->daddr);

    /* Set an offset for source and destination address. */
	DMA0->TCD[ch].SOFF =cfg->soff;
	DMA0->TCD[ch].DOFF =cfg->doff;

	/* Set source and destination data transfer size in byte. */
	DMA0->TCD[ch].ATTR = DMA_ATTR_SSIZE(size2code(cfg->nbytes)) 
                        |DMA_ATTR_DSIZE(size2code(cfg->nbytes));

	/*Number of bytes to be transfered in each service request of the channel.*/
	DMA0->TCD[ch].NBYTES_MLNO= cfg->nbytes;

	/* Current major iteration count. */
	DMA0->TCD[ch].CITER_ELINKNO = DMA_CITER_ELINKNO_CITER(cfg->major_count);
	DMA0->TCD[ch].BITER_ELINKNO = DMA_BITER_ELINKNO_BITER(cfg->major_count);

	/* Address for the next TCD to be loaded in the scatter/gather mode. */
	//	tcd[TCD0].SLAST = 0;			// Source address adjustment not used.
	//	tcd[TCD0].DLASTSGA = (uint32_t)&tcd[TCD1];	// The tcd[TCD1] is the next TCD to be loaded.

	DMA0->TCD[ch].SLAST = cfg->slast;
	DMA0->TCD[ch].DLAST_SGA = cfg->dlast;

	/* Setup control and status register. */
    if (cfg->int_major)
    {
	    DMA0->TCD[ch].CSR = DMA_CSR_INTMAJOR_MASK;	//Enable Major Interrupt.
    }

    return 0;
}

int DMA_Start(uint8_t ch)
{
    if (!initialized) return -4;
    if (ch >= DMA_NUM_CH) return -1;

    dma_ch_states[ch].active = true;

    /* Clear pending int/err, then safely enable ERQ for this channel */
    DMA0->CINT = DMA_CINT_CINT(ch);
    DMA0->CERR = DMA_CERR_CERR(ch);
    DMA0->SERQ = DMA_SERQ_SERQ(ch);   /* sets ERQ bit without touching others */
    return 0;
}

int DMA_Stop(uint8_t ch)
{
    if (!initialized) return -4;
    if (ch >= DMA_NUM_CH) return -1;

    dma_ch_states[ch].active = false;

    DMA0->CERQ = DMA_CERQ_CERQ(ch);  /* clears ERQ bit for this channel only */
    return 0;
}

static int size2code(uint8_t bytes) 
{
    switch (bytes) 
    { 
        case 1: return 0; 
        case 2: return 1; 
        case 4: return 2; 
    }
    return -1;
}

static void DMA_IRQHandler(uint8_t ch)
{
    gpioWrite(PIN_TP3, HIGH);
	/* Clear the interrupt flag. */
	DMA0->CINT |= DMA_CINT_CINT(ch);
	if(dma_ch_states[ch].on_major_cb)
    {
		dma_ch_states[ch].on_major_cb(dma_ch_states[ch].user_param);
	}
    gpioWrite(PIN_TP3, LOW);
}

void DMA0_IRQHandler(void){ DMA_IRQHandler(0); }
void DMA1_IRQHandler(void){ DMA_IRQHandler(1); }
void DMA2_IRQHandler(void){ DMA_IRQHandler(2); }
void DMA3_IRQHandler(void){ DMA_IRQHandler(3); }
void DMA4_IRQHandler(void){ DMA_IRQHandler(4); }
void DMA5_IRQHandler(void){ DMA_IRQHandler(5); }
void DMA6_IRQHandler(void){ DMA_IRQHandler(6); }
void DMA7_IRQHandler(void){ DMA_IRQHandler(7); }
void DMA8_IRQHandler(void){ DMA_IRQHandler(8); }
void DMA9_IRQHandler(void){ DMA_IRQHandler(9); }
void DMA10_IRQHandler(void){ DMA_IRQHandler(10); }
void DMA11_IRQHandler(void){ DMA_IRQHandler(11); }
void DMA12_IRQHandler(void){ DMA_IRQHandler(12); }
void DMA13_IRQHandler(void){ DMA_IRQHandler(13); }
void DMA14_IRQHandler(void){ DMA_IRQHandler(14); }
void DMA15_IRQHandler(void){ DMA_IRQHandler(15); }

// ToDo implement a error handler
// void DMA_Error_IRQHandler(void)
// {
// 	/* Clear the error interrupt flag.*/
// 	DMA0->CERR |= 0;

// 	/* Turn the red LED on. */
// 	PTB->PTOR |= (1 << PIN_RED_LED);
// }