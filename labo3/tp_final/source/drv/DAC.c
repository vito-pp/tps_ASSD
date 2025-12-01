/**
 * @file    DAC.c
 * @brief   Driver mínimo de DAC para Kinetis (DAC0/DAC1): init y escritura de 
 * dato.
 * @note    Habilita clock y configura referencia/trigger por software.
 */

#include "DAC.h"

#define DAC_DATL_DATA0_WIDTH 8

void DAC_Init (void)
{
	SIM->SCGC2 |= SIM_SCGC2_DAC0_MASK;
	SIM->SCGC2 |= SIM_SCGC2_DAC1_MASK;

	DAC0->C0 = DAC_C0_DACEN_MASK | DAC_C0_DACRFS_MASK | DAC_C0_DACTRGSEL_MASK;
	DAC1->C0 = DAC_C0_DACEN_MASK | DAC_C0_DACRFS_MASK | DAC_C0_DACTRGSEL_MASK;
}

void DAC_SetData (DAC_t dac, DACData_t data)
{
	dac->DAT[0].DATL = DAC_DATL_DATA0(data);
	dac->DAT[0].DATH = DAC_DATH_DATA1(data >> DAC_DATL_DATA0_WIDTH);
}

