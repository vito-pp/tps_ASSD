/***************************************************************************//**
  @file     board.h
  @brief    Board management for the FRDM-K64F
  @author   Nicolás Magliola
 ******************************************************************************/

#ifndef _BOARD_H_
#define _BOARD_H_

/*******************************************************************************
 * INCLUDE HEADER FILES
 ******************************************************************************/

#include "gpio.h"

/*******************************************************************************
 * CONSTANT AND MACRO DEFINITIONS USING #DEFINE
 ******************************************************************************/

/***** BOARD defines **********************************************************/

// On Board User LEDs
#define PIN_LED_RED     PORTNUM2PIN(PB, 22)   // PTB22
#define PIN_LED_GREEN   PORTNUM2PIN(PE, 26)   // PTE26
#define PIN_LED_BLUE    PORTNUM2PIN(PB, 21)   // PTB21

#define PIN_TP1         PORTNUM2PIN(PB, 2)             
#define PIN_TP2         PORTNUM2PIN(PB, 3)   
#define PIN_TP3         PORTNUM2PIN(PB, 10)
#define PIN_TP4         PORTNUM2PIN(PB, 11)             

#define LED_ACTIVE      LOW

// On Board User Switches
#define PIN_SW2         // ???
#define PIN_SW3         PORTNUM2PIN(PA, 4)    // PTA4

#define SW_ACTIVE       LOW 
#define SW_INPUT_TYPE   // ???

#define PIN_I2C_SCL     PORTNUM2PIN(PE, 24)
#define PIN_I2C_SDA     PORTNUM2PIN(PE, 25)

/*******************************************************************************
 ******************************************************************************/

#endif // _BOARD_H_
