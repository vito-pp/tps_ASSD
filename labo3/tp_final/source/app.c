/***************************************************************************//**
  @file     app.c
  @brief    Implementation of a FFT on a FRDM K64F dev board. Samples a signal
  through the ADC and then outputs the FFTs magnitude with the DAC.
 ******************************************************************************/

/*******************************************************************************
 * INCLUDE HEADER FILES
 ******************************************************************************/

#include "drv/board.h"
#include "drv/gpio.h"
#include "drv/ADC.h"
#include "drv/DAC.h"
#include "drv/dma.h"
#include "drv/pit.h"
#include "fft.h"
#include "hardware.h"

#include <math.h>

/*******************************************************************************
 * CONSTANT AND MACRO DEFINITIONS USING #DEFINE
 ******************************************************************************/

#define ADC_BITS 12
#define ADC_MAX ((1 << ADC_BITS) - 1)
#define ADC_MID (ADC_MAX/2)
#define ADC_SCALE (1.0f / (float)ADC_MID)

/*******************************************************************************
 * FILE LEVEL SCOPE VARIABLES
 ******************************************************************************/

static volatile uint16_t adc_buf[2][FFT_SIZE]; // ping pong buffering
static volatile bool is_buf_ready[2] = {false, false};
static volatile uint8_t current_buf = 0;

static complex float fft_in[FFT_SIZE], fft_out[FFT_SIZE];

static uint16_t dac_buf[FFT_SIZE/2];

/*******************************************************************************
 * FUNCTION PROTOTYPES FOR PRIVATE FUNCTIONS WITH FILE LEVEL SCOPE
 ******************************************************************************/
// callbacks
void adcDmaCallback(void *user);
void dacDmaCallback(void *user);
void pitCallback(void *user);

// helper functions
void adcBufToComplex(volatile uint16_t *adc_buf, complex float *fft_in);
void computeMagnitude(complex float *fft_out, uint16_t *dac_buf);

/*******************************************************************************
 *******************************************************************************
                        GLOBAL FUNCTION DEFINITIONS
 *******************************************************************************
 ******************************************************************************/

void App_Init (void)
{
    // GPIOs init
    gpioMode(PIN_LED_BLUE, OUTPUT);
    gpioWrite(PIN_LED_BLUE, !LED_ACTIVE);
    gpioMode(PIN_LED_RED, OUTPUT);
    gpioWrite(PIN_LED_RED, !LED_ACTIVE);
    gpioMode(PIN_TP69, OUTPUT);

    DMA_Init();
    PIT_Init();
    ADC_Init(true); // dma request = true
    DAC_Init();

    // DMA configs
    dma_cfg_t dma_adc_cfg =
    {
        .ch = 0,
        .request_src = DMA_REQ_ADC0,
        .trig_mode = false,
        .saddr = (void *)&ADC0->R[0],
        .daddr = (void *)&adc_buf[0][0],
        .nbytes = sizeof(uint16_t),
        .soff = 0, 
        .doff = sizeof(uint16_t),
        .major_count = FFT_SIZE,
        .slast = 0,
        .dlast = 0, // major loop cb changes the daddr
        .int_major = true,
        .on_major = adcDmaCallback,
        .user = NULL
    };
    DMA_Config(&dma_adc_cfg);
    DMA_Start(0);

    dma_cfg_t dma_dac_cfg =
    {
        .ch = 1,
        .request_src = DMA_REQ_ALWAYS63,
        .trig_mode = true, // PIT ch1 will trigger this dma req
        .saddr = (void*)&dac_buf[0],
        .daddr = (void*)&DAC0->DAT[0].DATL,
        .nbytes = sizeof(uint16_t),
        .soff = sizeof(uint16_t), 
        .doff = 0,
        .major_count = FFT_SIZE/2,
        .slast = -(uint32_t)(FFT_SIZE/2 * sizeof(uint16_t)),
        .dlast = 0,
        .int_major = true,
        .on_major = dacDmaCallback,
        .user = NULL
    };
    DMA_Config(&dma_dac_cfg);
    DMA_Start(1);

    // PIT configs
    pit_cfg_t pit_adc_cfg =
    {
        .ch = 0,
        .load_val = PIT_TICKS_FROM_US(83), // 12kHz ADC sampling rate
        .periodic = true,
        .int_en = true,
        .dma_req = false,
        .callback = pitCallback, // PIT starts ADC's start of conversion
        .user = NULL
    };
    PIT_Config(&pit_adc_cfg);

    pit_cfg_t pit_dac_cfg =
    {
        .ch = 1,
        .load_val = PIT_TICKS_FROM_US(100), // 10kHz DAC transfer rate
        .periodic = true,
        .int_en = true,
        .dma_req = true,
        .callback = NULL,
        .user = NULL
    };
    PIT_Config(&pit_dac_cfg);
}

void App_Run (void)
{
    int8_t buf_idx = -1;

    hw_DisableInterrupts(); // avoid race conditions for is_buf_ready
    if (is_buf_ready[0]) 
    {
        buf_idx = 0;
        is_buf_ready[0] = false;
    }
    else if (is_buf_ready[1]) 
    {
        buf_idx = 1;
        is_buf_ready[1] = false;
    }
    hw_EnableInterrupts();

    if (buf_idx >= 0)
    { 
        adcBufToComplex(adc_buf[buf_idx], fft_in);
        fft(fft_in, fft_out);
        computeMagnitude(fft_out, dac_buf);
    }
}


/*******************************************************************************
 *******************************************************************************
                        LOCAL FUNCTION DEFINITIONS
 *******************************************************************************
 ******************************************************************************/

void adcDmaCallback(void *user)
{
    uint8_t filled = current_buf;
    is_buf_ready[filled] = true;
    current_buf ^= 1; // flip buffer

    // point DADDR to the new buffer
    uint8_t ch = 0; // same channel as above
    DMA0->TCD[ch].DADDR = (uint32_t)&adc_buf[current_buf][0];

    // reload loop counters
    DMA0->TCD[ch].CITER_ELINKNO = FFT_SIZE;
    DMA0->TCD[ch].BITER_ELINKNO = FFT_SIZE;
}

void dacDmaCallback(void *user)
{
    gpioToggle(PIN_TP69);
}

void pitCallback(void *user)
{
    ADC_Start(ADC0, 1, ADC_mA); // start of conversion
}

void adcBufToComplex(volatile uint16_t *adc_buf, complex float *fft_in)
{
    for (size_t i = 0; i < FFT_SIZE; i++)
    {
        int32_t centered = (int32_t)adc_buf[i] - (int32_t)ADC_MID; // remove DC
        float x = (float)centered * ADC_SCALE; // [-1, 1]

        // Optional: apply window here for less spectral leakage
        // x *= window[i];

        fft_in[i] = x + 0.0f*I;
    }
}

void computeMagnitude(complex float *fft_out, uint16_t *dac_buf)
{
    const size_t N = FFT_SIZE;
    float mag[N/2];
    float max_mag = 0.0f;

    // compute magnitudes (one-sided spectrum)
    for (size_t k = 0; k < N/2; k++)
    {
    	float re = ((float *)&fft_out[k])[0];
    	float im = ((float *)&fft_out[k])[1];
    	float m  = sqrtf(re*re + im*im);

        mag[k] = m;
        if (m > max_mag) max_mag = m;
    }

    if (max_mag < 1e-9f) max_mag = 1.0f;  // avoid divide-by-zero

    // normalize
    for (size_t k = 0; k < N/2; k++)
    {
        float norm = mag[k] / max_mag;  // 0..1
        if (norm < 0.0f) norm = 0.0f; // just to be sure, clamp norm
        if (norm > 1.0f) norm = 1.0f;

        dac_buf[k] = (uint16_t)(norm * 4095.0f);
    }

    // Optionally: force DC bin to a fixed level for easier triggering
    // dac_buf[0] = 0; or 4095; etc.
}


/*******************************************************************************
 ******************************************************************************/
