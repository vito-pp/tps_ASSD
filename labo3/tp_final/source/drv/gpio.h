/***************************************************************************//**
  @file     gpio.h
  @brief    Simple GPIO Pin services, similar to Arduino
  @author   Nicolás Magliola
 ******************************************************************************/

#ifndef _GPIO_H_
#define _GPIO_H_

/*******************************************************************************
 * INCLUDE HEADER FILES
 ******************************************************************************/

#include <stdint.h>
#include <stdbool.h>

/*******************************************************************************
 * CONSTANT AND MACRO DEFINITIONS USING #DEFINE
 ******************************************************************************/

// Convert port and number into pin ID
// Ex: PTB5  -> PORTNUM2PIN(PB,5)  -> 0x25
//     PTC22 -> PORTNUM2PIN(PC,22) -> 0x56
#define PORTNUM2PIN(p,n)    (((p)<<5) + (n))
#define PIN2PORT(p)         (((p)>>5) & 0x07)
#define PIN2NUM(p)          ((p) & 0x1F)

// Modes
#ifndef INPUT
#define INPUT               0
#define OUTPUT              1
#define INPUT_PULLUP        2
#define INPUT_PULLDOWN      3
#endif // INPUT

// Digital values
#ifndef LOW
#define LOW     0
#define HIGH    1
#endif // LOW

#define NUM_PORTS 5
#define PINS_PER_PORT 32

// Ports
enum { PA, PB, PC, PD, PE };

// PCRn: MUX options
typedef enum
{
	ALT0, // analog
	ALT1, // GPIO 
	ALT2,
	ALT3,
	ALT4,
	ALT5,
	ALT6,
	ALT7,
} pcr_mux_option_t;

// PCRn: IRQC options
typedef enum {
	PORT_PCR_IRQC_DISABLED 		= 0x00,        
	PORT_PCR_IRQC_DMA_RISING    = 0x01,
	PORT_PCR_IRQC_DMA_FALLING   = 0x02,  
	PORT_PCR_IRQC_DMA_EITHER    = 0x03,  
	PORT_PCR_IRQC_INT_LOW       = 0x08,  
	PORT_PCR_IRQC_INT_RISING    = 0x09,  
	PORT_PCR_IRQC_INT_FALLING   = 0x0A,  
	PORT_PCR_IRQC_INT_EITHER    = 0x0B,  
	PORT_PCR_IRQC_INT_HIGH      = 0x0C,
} irq_mode_t;

/*******************************************************************************
 * ENUMERATIONS AND STRUCTURES AND TYPEDEFS
 ******************************************************************************/

typedef uint8_t pin_t;

typedef void (*pinIrqFun_t)(void);

/*******************************************************************************
 * VARIABLE PROTOTYPES WITH GLOBAL SCOPE
 ******************************************************************************/

/*******************************************************************************
 * FUNCTION PROTOTYPES WITH GLOBAL SCOPE
 ******************************************************************************/

/**
 * @brief Configures the specified pin to behave either as an input or an output
 * @param pin the pin whose mode you wish to set (according PORTNUM2PIN)
 * @param mode INPUT, OUTPUT, INPUT_PULLUP or INPUT_PULLDOWN.
 */
void gpioMode (pin_t pin, uint8_t mode);

/**
 * @brief Write a HIGH or a LOW value to a digital pin
 * @param pin the pin to write (according PORTNUM2PIN)
 * @param val Desired value (HIGH or LOW)
 */
void gpioWrite (pin_t pin, bool value);

/**
 * @brief Toggle the value of a digital pin (HIGH<->LOW)
 * @param pin the pin to toggle (according PORTNUM2PIN)
 */
void gpioToggle (pin_t pin);

/**
 * @brief Reads the value from a specified digital pin, either HIGH or LOW.
 * @param pin the pin to read (according PORTNUM2PIN)
 * @return HIGH or LOW
 */
bool gpioRead (pin_t pin);

/**
 * @brief Configures how the pin reacts when an IRQ event ocurrs
 * @param pin the pin whose IRQ mode you wish to set (according PORTNUM2PIN)
 * @param irqMode disable, risingEdge, fallingEdge or bothEdges
 * @param irqFun function to call on pin event
 * @return Registration succeed
 */
bool gpioIRQ (pin_t pin, irq_mode_t irqMode, pinIrqFun_t irqFun);

/*******************************************************************************
 ******************************************************************************/

#endif // _GPIO_H_
