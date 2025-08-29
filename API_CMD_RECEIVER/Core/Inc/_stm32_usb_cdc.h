/*
 * _stm32_usb_cdc.h
 *
 *  Created on: Aug 28, 2025
 *      Author: Ev Hoang
 */
#ifndef INC__STM32_USB_CDC_H_
#define INC__STM32_USB_CDC_H_

#ifdef __cplusplus
extern "C" {
#endif

#define RX_BUF_SIZE 64

#include "stm32f1xx.h"

extern char usb_rx_buffer[RX_BUF_SIZE];
extern uint16_t usb_rx_index;
extern uint8_t uart_line_ready;


#ifdef __cplusplus
}
#endif

#endif /* INC__STM32_USB_CDC_H_ */
