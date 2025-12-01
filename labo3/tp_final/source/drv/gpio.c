/***************************************************************************//**
  @file     gpio.c
  @brief    Simple GPIO Pin services, similar to Arduino
 ******************************************************************************/

/*******************************************************************************
 * INCLUDE HEADER FILES
 ******************************************************************************/

#include <stddef.h>
#include "MK64F12.h"
#include "gpio.h"
#include "hardware.h"

/*******************************************************************************
 * CONSTANT AND MACRO DEFINITIONS USING #DEFINE
 ******************************************************************************/

static PORT_Type * const kPort[] = PORT_BASE_PTRS;
static GPIO_Type * const kGpio[] = GPIO_BASE_PTRS;

#define IRQn_PORTS_BASE PORTA_IRQn

/*******************************************************************************
 * FILE SCOPE VARIABLES
 ******************************************************************************/

pinIrqFun_t callback_tbl[NUM_PORTS][PINS_PER_PORT];

/*******************************************************************************
 *******************************************************************************
                        GLOBAL FUNCTION DEFINITIONS
 *******************************************************************************
 ******************************************************************************/

void gpioMode (pin_t pin, uint8_t mode)
{
  //1) set MUX, PE and PS to known state, i.e. logical 0
  kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] &= ~(PORT_PCR_MUX(0b111)
                                              |PORT_PCR_PS(0b1)
                                              |PORT_PCR_PE(0b1));

  //2) PCRn mux: set MUX bits to ALT1 = GPIO
  kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] |= PORT_PCR_MUX(ALT1);

  //3) GPIO direction, pullups and pulldowns
  if (mode == OUTPUT)
    kGpio[PIN2PORT(pin)]->PDDR |= 1 << PIN2NUM(pin);
  else
    kGpio[PIN2PORT(pin)]->PDDR &= ~(1 << PIN2NUM(pin));

  // pull enable
  if (mode == INPUT_PULLDOWN || mode == INPUT_PULLDOWN)
    kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] |= PORT_PCR_PE(0b1);
  else
    kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] &= ~PORT_PCR_PE(0b1);

  // pull select
  if (mode == INPUT_PULLUP)
    kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] |= PORT_PCR_PS(0b1);
  else if (mode == INPUT_PULLDOWN)
    kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] &= ~PORT_PCR_PS(0b1);
}

void gpioWrite (pin_t pin, bool value)
{
  if (value)
    kGpio[PIN2PORT(pin)]->PSOR |= 1 << PIN2NUM(pin); // sets bit to 1
  else
    kGpio[PIN2PORT(pin)]->PCOR |= 1 << PIN2NUM(pin); // clears bit to 0
}

void gpioToggle (pin_t pin)
{
  kGpio[PIN2PORT(pin)]->PTOR |= 1 << PIN2NUM(pin);
}

bool gpioRead (pin_t pin)
{
	int x =  1 && (kGpio[PIN2PORT(pin)]->PDIR) & (1 << PIN2NUM(pin));
	return x;
}

bool gpioIRQ (pin_t pin, irq_mode_t irqMode, pinIrqFun_t irqFun)
{
  if (irqFun == NULL) return false;

  // sets IRQC to known state, i.e. 0000
  kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] &= ~PORT_PCR_IRQC(0b1111);
  // sets IRQC to the specified mode
  kPort[PIN2PORT(pin)]->PCR[PIN2NUM(pin)] |= PORT_PCR_IRQC(irqMode);

  // enable the IRQ through NVIC's ISER register
  __NVIC_EnableIRQ(IRQn_PORTS_BASE + PIN2PORT(pin));
  
  callback_tbl[PIN2PORT(pin)][PIN2NUM(pin)] = irqFun;
  return true;
}

void PORTA_IRQHandler(void)
{
    for (int i = 0; i < PINS_PER_PORT; i++)
    {
        if (PORTA->ISFR & (1 << i))
        {
            PORTA->ISFR = 1 << i;

            callback_tbl[PA][i]();
        }
    }
}

void PORTB_IRQHandler(void)
{
    for (int i = 0; i < PINS_PER_PORT; i++)
    {
        if (PORTB->ISFR & (1 << i))
        {
            PORTB->ISFR = 1 << i;

            callback_tbl[PB][i]();
        }
    }
}

void PORTC_IRQHandler(void)
{
    for (int i = 0; i < PINS_PER_PORT; i++)
    {
        if (PORTC->ISFR & (1 << i))
        {
            PORTC->ISFR = 1 << i;

            callback_tbl[PC][i]();
        }
    }
}

void PORTD_IRQHandler(void)
{
    for (int i = 0; i < PINS_PER_PORT; i++)
    {
        if (PORTD->ISFR & (1 << i))
        {
            PORTD->ISFR = 1 << i;

            callback_tbl[PD][i]();
        }
    }
}

void PORTE_IRQHandler(void)
{
    for (int i = 0; i < PINS_PER_PORT; i++)
    {
        if (PORTE->ISFR & (1 << i))
        {
            PORTE->ISFR = 1 << i;

            callback_tbl[PE][i]();
        }
    }
}
