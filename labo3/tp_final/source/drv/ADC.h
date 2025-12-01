/**
 * @file ADC.h
 * @brief ADC driver for Kinetis (ADC0/ADC1): init, resolution/cycles config, 
 * hardware averaging, calibration, trigger and read.
 *
 * Enables clocks and NVIC and initializes ADC0 by default. Includes 
 * calibration routine.
 */

#ifndef SOURCES_TEMPLATE_ADC_H_
#define SOURCES_TEMPLATE_ADC_H_

#include "hardware.h"
#include "MK64F12.h"

typedef enum
{
    ADC_b8,
    ADC_b12,
    ADC_b10,
    ADC_b16,
} ADCBits_t;

typedef enum
{
    ADC_c24,
    ADC_c16,
    ADC_c10,
    ADC_c6,
    ADC_c4,
} ADCCycles_t;

typedef enum
{
    ADC_t4,
    ADC_t8,
    ADC_t16,
    ADC_t32,
    ADC_t1,
} ADCTaps_t;

typedef enum
{
    ADC_mA,
    ADC_mB,
} ADCMux_t;

typedef ADC_Type *ADC_t;
typedef uint8_t ADCChannel_t; /* Channel 0-23 */
typedef uint16_t ADCData_t;

/**
 * @brief Initialize the ADC subsystem (ADC0/ADC1) and configure ADC0 by 
 * default.
 *
 * - Enables clocks for ADC0 and ADC1.
 * - Enables NVIC interrupts for ADC.
 * - Configures prescaler / base settings (CFG1).
 * - Sets ADC0 resolution and sample cycles.
 * - Performs ADC0 calibration.
 *
 * @post ADC0 is ready to perform conversions with the selected resolution/
 * cycles.
 *
 * @param dma_req  true to enable DMA request mode during init, false otherwise.
 */
void 		ADC_Init 			   (bool dma_req);

/**
 * @brief Enable or disable end-of-conversion interrupt mode for an ADC.
 *
 * @param adc   ADC0 or ADC1 peripheral pointer.
 * @param mode  true to enable interrupt, false to disable.
 *
 * @note Updates an internal flag used when starting conversions (SC1.AIEN).
 */
void 		ADC_SetInterruptMode   (ADC_t, bool);

/**
 * @brief Check whether an end-of-conversion interrupt is pending (COCO=1) on 
 * SC1[0].
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return true if COCO==1, false otherwise.
 *
 * @note Reads SC1[0] and evaluates the COCO bit.
 */
bool 		ADC_IsInterruptPending (ADC_t);

/**
 * @brief Clear the conversion-complete flag for SC1[0].
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 *
 * @note Writes SC1[0] to clear COCO as described in the reference manual.
 */
void 		ADC_ClearInterruptFlag (ADC_t);

/**
 * @brief Set the ADC conversion resolution (8/10/12/16 bits, as supported by 
 * the SoC).
 *
 * @param adc   ADC0 or ADC1 peripheral pointer.
 * @param bits  Resolution mode (enum ADCBits_t).
 *
 * @note Updates the MODE field in CFG1.
 */
void 		ADC_SetResolution 	   (ADC_t, ADCBits_t);

/**
 * @brief Get the currently configured ADC resolution.
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return ADCBits_t Current MODE field value from CFG1.
 */
ADCBits_t 	ADC_GetResolution 	   (ADC_t);

/**
 * @brief Configure ADC sample time (number of cycles).
 *
 * @param adc     ADC0 or ADC1 peripheral pointer.
 * @param cycles  Sample cycles selection (enum ADCCycles_t).
 *
 * @details If the selected value requires long sampling, enable ADLSMP and set ADLSTS.
 *          Otherwise disable long sampling.
 */
void 		ADC_SetCycles	 	   (ADC_t, ADCCycles_t);

/**
 * @brief Return the active sample cycles configuration.
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return ADCCycles_t Corresponding to the current sample time configuration.
 *
 * @note If ADLSMP==1 returns ADC_c4 (long sample); otherwise uses ADLSTS to determine cycles.
 */
ADCCycles_t ADC_GetCycles	 	   (ADC_t);

/**
 * @brief Configure hardware averaging for the ADC.
 *
 * @param adc   ADC0 or ADC1 peripheral pointer.
 * @param taps  Number of samples to average (enum ADCTaps_t).
 *
 * @details If @p taps is invalid, hardware averaging is disabled (AVGE=0).
 *          Otherwise AVGE is enabled and AVGS is programmed accordingly.
 */
void 		ADC_SetHardwareAverage (ADC_t, ADCTaps_t);

/**
 * @brief Query whether hardware averaging is active and its configuration.
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return ADCTaps_t If AVGE==1 returns the configured taps value; otherwise 
 * returns ADC_t1 indicating averaging disabled.
 */
ADCTaps_t   ADC_GetHardwareAverage (ADC_t);

/**
 * @brief Perform ADC calibration routine.
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return true if calibration completes without errors; false if CALF 
 * (calibration failed) is detected.
 *
 * @details
 * - Runs the calibration sequence and checks the CALF flag.
 * - Computes PG/MG from the sum of calibration coefficients (CLPx/CLMx).
 * - Performs additional iterations (2^4) to refine OFS/gain values.
 * - Restores original SC3 on completion.
 *
 * @post PG, MG, OFS and calibration coefficients CLP/CLM* are updated.
 */
bool 		ADC_Calibrate 		   (ADC_t);

/**
 * @brief Trigger a conversion on the specified channel.
 *
 * @param adc      ADC0 or ADC1 peripheral pointer.
 * @param channel  Channel to convert (ADCChannel_t).
 * @param mux      Mux selection (ADCMux_t).
 *
 * @note Adjusts MUXSEL (CFG2) and writes SC1[0] with ADCH and AIEN according 
 * to internal interrupt flag.
 */
void 		ADC_Start 			   (ADC_t, ADCChannel_t, ADCMux_t);

/**
 * @brief Check if the current conversion has finished (COCO==1).
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return true if COCO==1, false otherwise.
 */
bool 		ADC_IsReady 	       (ADC_t);

/**
 * @brief Read the converted result from R[0].
 *
 * @param adc  ADC0 or ADC1 peripheral pointer.
 * @return ADCData_t Converted sample.
 *
 * @note Must be called after COCO indicates conversion completion.
 */
ADCData_t 	ADC_getData 		   (ADC_t);

#endif /* SOURCES_TEMPLATE_ADC_H_ */