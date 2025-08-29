
#include "main.h"
#include "usb_device.h"
#include "_stm32_usb_cdc.h"

void CDC_Transmit(char *msg)
{
    uint16_t len = strlen(msg);
    uint8_t status;
    do {
        status = CDC_Transmit_FS((uint8_t*)msg, len);
    } while (status == USBD_BUSY);
}

void Timer_Start(void) {
    TIM2->CNT = 0;              // reset counter về 0
    TIM2->CR1 |= TIM_CR1_CEN;   // bật timer
}

void Timer_Stop(void) {
    TIM2->CR1 &= ~TIM_CR1_CEN;  // tắt timer
    TIM2->CNT = 0;              // reset counter về 0 (nếu muốn)
}

int cur_pos = 1;
int max_pos = 10;

int led_buf_l[10] = {0,0,0,0,0,0,0,0,0,0};
int led_buf_r[10] = {11,11,11,11,11,11,11,11,11,11};
int buf_pos = 0;

void CHECK_CMD(char *buf) {
	int cmd = 0;
    if (strcmp(buf, "SW_L") == 0) cmd = 1;
    else if (strcmp(buf, "SW_R") == 0) cmd = 2;
    else if (strcmp(buf, "ACT") == 0) cmd = 3;

    switch(cmd) {
    case 2: {
    	if(cur_pos >= max_pos) break;
    	GPIOA->BRR = 1 << cur_pos;
    	cur_pos++;
    	GPIOA->BSRR = 1 << cur_pos;
    	break;
    }
    case 1: {
    	if(cur_pos <= 1) break;
    	GPIOA->BRR = 1 << cur_pos;
    	cur_pos--;
    	GPIOA->BSRR = 1 << cur_pos;
    	break;
    }
    case 3: {
    	buf_pos = (buf_pos + 1)%10;
    	led_buf_l[buf_pos] = cur_pos - 1;
    	led_buf_r[buf_pos] = cur_pos + 1;
    	if(led_buf_l[buf_pos] > 0) GPIOA->BSRR = 1 << led_buf_l[buf_pos];
    	if(led_buf_r[buf_pos] <= max_pos) GPIOA->BSRR = 1 << led_buf_r[buf_pos];
    	break;
    }
    }
}

void TIM2_IRQHandler(void)
{
    if (TIM2->SR & TIM_SR_UIF)
    {
        TIM2->SR &= ~TIM_SR_UIF;
        for(int i = 0 ; i < 10; i++) {
        	if(led_buf_l[i] > 0) {
        		GPIOA->BRR = 1 << led_buf_l[i];
        		led_buf_l[i]--;
        		GPIOA->BSRR = 1 << led_buf_l[i];
        	}

        	if(led_buf_r[i] <= max_pos) {
				GPIOA->BRR = 1 << led_buf_r[i];
				led_buf_r[i]++;
				GPIOA->BSRR = 1 << led_buf_r[i];
			}
        }
        GPIOA->BSRR = 1 << cur_pos;
    }
}

int main(void)
{
	SystemClock_Config();
	MX_USB_DEVICE_Init();
	GPIO_Init();
	TIM2_Init();

	GPIOA->BSRR = 1 << cur_pos;
  while (1)
  {
	  if(uart_line_ready) {
		  uart_line_ready = 0;
		  CHECK_CMD(usb_rx_buffer);
	  }
  }
}


void SystemClock_Config(void)
{
    // 1. Bật HSE
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY));  // Chờ HSE ổn định

    // 2. Cấu hình Flash: Prefetch + 2 wait states (72 MHz)
    FLASH->ACR |= FLASH_ACR_PRFTBE;     // Prefetch buffer enable
    FLASH->ACR &= ~FLASH_ACR_LATENCY;
    FLASH->ACR |= FLASH_ACR_LATENCY_2;  // 2 wait states

    // 3. Cấu hình Prescaler
    RCC->CFGR |= RCC_CFGR_HPRE_DIV1;    // AHB = SYSCLK / 1 = 72 MHz
    RCC->CFGR |= RCC_CFGR_PPRE1_DIV2;   // APB1 = SYSCLK / 2 = 36 MHz (max 36 MHz)
    RCC->CFGR |= RCC_CFGR_PPRE2_DIV1;   // APB2 = SYSCLK / 1 = 72 MHz

    // 4. Cấu hình PLL: nguồn = HSE, hệ số nhân x9 → 8*9=72 MHz
    RCC->CFGR &= ~RCC_CFGR_PLLSRC;      // Clear
    RCC->CFGR |= RCC_CFGR_PLLSRC;       // PLL source = HSE
    RCC->CFGR &= ~RCC_CFGR_PLLMULL;     // Clear multiplier
    RCC->CFGR |= RCC_CFGR_PLLMULL9;     // PLL = HSE * 9

    // 5. USB clock = PLL / 1.5 = 48 MHz
    RCC->CFGR &= ~RCC_CFGR_USBPRE;      // USBPRE = 0 → divide by 1.5

    // 6. Bật PLL
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY)); // Chờ PLL ổn định

    // 7. Chọn PLL làm SYSCLK
    RCC->CFGR &= ~RCC_CFGR_SW;
    RCC->CFGR |= RCC_CFGR_SW_PLL;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL); // Chờ PLL được chọn

    // Bây giờ: SYSCLK = 72 MHz, USBCLK = 48 MHz
}

void GPIO_Init(void)
{
    // 1. Bật clock cho PORTA
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;

    // 2. Clear cấu hình cũ cho PA1 -> PA10
    GPIOA->CRL &= ~((0xF << (1 * 4)) |   // PA1
                    (0xF << (2 * 4)) |   // PA2
                    (0xF << (3 * 4)) |   // PA3
                    (0xF << (4 * 4)) |   // PA4
                    (0xF << (5 * 4)) |   // PA5
                    (0xF << (6 * 4)) |   // PA6
                    (0xF << (7 * 4)));   // PA7

    GPIOA->CRH &= ~((0xF << ((8 - 8) * 4)) |   // PA8
                    (0xF << ((9 - 8) * 4)) |   // PA9
                    (0xF << ((10 - 8) * 4)));  // PA10

    // 3. Set MODE=10, CNF=00 -> 0x2 cho PA1 -> PA10
    GPIOA->CRL |=  ((0x2 << (1 * 4)) |
                    (0x2 << (2 * 4)) |
                    (0x2 << (3 * 4)) |
                    (0x2 << (4 * 4)) |
                    (0x2 << (5 * 4)) |
                    (0x2 << (6 * 4)) |
                    (0x2 << (7 * 4)));

    GPIOA->CRH |=  ((0x2 << ((8 - 8) * 4)) |
                    (0x2 << ((9 - 8) * 4)) |
                    (0x2 << ((10 - 8) * 4)));

    // 4. Reset output về mức 0 ban đầu
    GPIOA->ODR &= ~((0x7FE));   // clear PA1..PA10 (bits 1->10)
}


void TIM2_Init(void)
{
    // 1. Bật clock cho TIM2
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    // 2. Reset TIM2
    TIM2->CR1 = 0;
    TIM2->PSC = 7199;    // prescaler -> 72MHz / 7200 = 10kHz
    TIM2->ARR = 999;     // auto-reload -> 10kHz / 1000 = 10Hz = 100ms

    // 3. Enable update interrupt
    TIM2->DIER |= TIM_DIER_UIE;

    // 4. Enable TIM2
    TIM2->CR1 |= TIM_CR1_CEN;

    // 5. Enable TIM2_IRQn trong NVIC
    NVIC_SetPriority(TIM2_IRQn, 2);
    NVIC_EnableIRQ(TIM2_IRQn);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}
