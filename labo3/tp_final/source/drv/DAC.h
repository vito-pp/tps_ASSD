/**
 * @file DAC.h
 * @brief DAC driver for Kinetis (DAC0/DAC1): initialization and output helpers.
 *
 * This header declares a minimal driver interface to initialize the on-chip
 * DACs and write conversion values. The implementation enables the DAC
 * peripheral clocks and programs control register C0 for operation using
 * VDDA as reference and software trigger mode.
 *
 * Conventions:
 * - DATL/DATH register pair is used to write the conversion value (split low/
 * high).
 * - The DAC resolution/format depends on the SoC and how DATL/DATH are written.
 */
#ifndef DAC_H_
#define DAC_H_

#include "hardware.h"
#include "MK64F12.h"

typedef DAC_Type *DAC_t;
typedef uint16_t DACData_t;

/**
 * @brief Initialize DAC0 and DAC1.
 *
 * - Enables DAC clocks (SIM_SCGC2).
 * - Configures C0:
 *     - DACEN: enable converter
 *     - DACRFS: select VDDA as reference
 *     - DACTRGSEL: select software trigger
 *
 * After this call the DACs are ready to accept conversion values via DAT 
 * registers.
 */
void DAC_Init(void);

/**
 * @brief Write a value to a DAC channel (DAC0/DAC1).
 *
 * @param dac   Pointer to DAC peripheral (DAC0 or DAC1).
 * @param data  Digital value to convert. Width/format must match DAC 
 * resolution.
 *
 * @note The function writes the value into DATL/DATH register pair (low/high 
 * bytes)
 *       as required by the peripheral.
 */
void DAC_SetData(DAC_t dac, DACData_t data);

/**
 * @brief DAC interrupt / service routine handler.
 *
 * To be called from the DAC IRQ handler when the peripheral triggers an 
 * interrupt
 * (if enabled). The implementation may handle flags, DMA handoff or user 
 * callbacks.
 */
void DAC_PISR(void);

#endif /* DAC_H_ */