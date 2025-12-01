/***************************************************************************//**
  @file     SysTick.c
  @brief    SysTick driver
 ******************************************************************************/

#include <stdbool.h>
#include <stddef.h>
#include "hardware.h"

#include "gpio.h"
#include "board.h"

#define NUM_BITS_SYSTICK_LOAD 24

static void (*cb)(void);

bool SysTick_Init (void (*funcallback)(void), uint32_t count)
{
    if(funcallback == NULL || count >= (1U << (NUM_BITS_SYSTICK_LOAD + 1))
    || count == 0) 
        return false;

    SysTick->CTRL = 0x00;
    SysTick->LOAD = count - 1; // core CLK @ 100 MHz
    SysTick->VAL = 0x00;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | 
                    SysTick_CTRL_TICKINT_Msk |
                    SysTick_CTRL_ENABLE_Msk;

    cb = funcallback;
    return true;
}

void SysTick_Handler (void)
{
    cb();
}

uint32_t getValue_SysTick(void)
{
    return SysTick->VAL;
}
