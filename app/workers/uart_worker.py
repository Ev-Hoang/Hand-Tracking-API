from app.services import uart

async def uart_worker():
    """
    worker read uart data from uart_rx_queue simultaneously 
    Input:
        None
    Output:
        None
    """
    print("UART worker started")
    while True:
        data = await uart.uart_rx_queue.get()
        uart.data_received(data)
        uart.uart_rx_queue.task_done()
