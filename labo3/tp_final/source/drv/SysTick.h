/***************************************************************************//**
  @file     SysTick.h
  @brief    SysTick driver
  @author   Nicolas Magliola
 ******************************************************************************/

#ifndef _SYSTICK_H_
#define _SYSTICK_H_

/*******************************************************************************
 * INCLUDE HEADER FILES
 ******************************************************************************/

#include <stdbool.h>
#include <stdint.h>

/*******************************************************************************
 * CONSTANT AND MACRO DEFINITIONS USING #DEFINE
 ******************************************************************************/

#define SYSTICK_ISR_FREQUENCY_HZ 2000U

/*******************************************************************************
 * ENUMERATIONS AND STRUCTURES AND TYPEDEFS
 ******************************************************************************/

/*******************************************************************************
 * VARIABLE PROTOTYPES WITH GLOBAL SCOPE
 ******************************************************************************/

/*******************************************************************************
 * FUNCTION PROTOTYPES WITH GLOBAL SCOPE
 ******************************************************************************/

/**
 * @brief Initialize SysTic driver
 * @param funcallback Function to be called every SysTick
 * @param count Counter number which will be decreased @ 100 MHz.
 *        So to get, e.g., 8 Hz (125 ms) count = 12'500'000. 
 *        f_systick = 100 MHz / count
 *        Count is nonnegative and cant be bigger than 
 *        2^(25)-1 = 33'554'431, which equals f_systick = 2.98 Hz
 * @return Initialization and registration succeed. funcallback = NULL or 
 * invalid count returns false
 */
bool SysTick_Init(void (*funcallback)(void), uint32_t count);

/**
 * @brief Gets the current value of the SysTick counter register
 * @return Value of the counter
 */
uint32_t getValue_SysTick(void);

/*******************************************************************************
 ******************************************************************************/

#endif // _SYSTICK_H_