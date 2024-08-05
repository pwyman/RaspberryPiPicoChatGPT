import json
import network
import time
import urequests
import constants

# Diplay Settings
from machine import Pin,SPI
import framebuf
import time

DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9




class OLED_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 128
        self.height = 64
        self.rotate = 180 #only 0 and 180 
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,2000_000)
        self.spi = SPI(1,20000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)
        self.init_display()
        
        self.white =   0xffff
        self.balck =   0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        time.sleep(0.001)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        
        self.write_cmd(0xAE)#turn off OLED display

        self.write_cmd(0x00)   #set lower column address
        self.write_cmd(0x10)   #set higher column address 

        self.write_cmd(0xB0)   #set page address 
      
        self.write_cmd(0xdc)    #et display start line 
        self.write_cmd(0x00) 
        self.write_cmd(0x81)    #contract control 
        self.write_cmd(0x6f)    #128
        self.write_cmd(0x21)    # Set Memory addressing mode (0x20/0x21) #
        if self.rotate == 0:
            self.write_cmd(0xa0)    #set segment remap
        elif self.rotate == 180:
            self.write_cmd(0xa1)
        self.write_cmd(0xc0)    #Com scan direction
        self.write_cmd(0xa4)   #Disable Entire Display On (0xA4/0xA5) 

        self.write_cmd(0xa6)    #normal / reverse
        self.write_cmd(0xa8)    #multiplex ratio 
        self.write_cmd(0x3f)    #duty = 1/64
  
        self.write_cmd(0xd3)    #set display offset 
        self.write_cmd(0x60)

        self.write_cmd(0xd5)    #set osc division 
        self.write_cmd(0x41)
    
        self.write_cmd(0xd9)    #set pre-charge period
        self.write_cmd(0x22)   

        self.write_cmd(0xdb)    #set vcomh 
        self.write_cmd(0x35)  
    
        self.write_cmd(0xad)    #set charge pump enable 
        self.write_cmd(0x8a)    #Set DC-DC enable (a=0:disable; a=1:enable)
        self.write_cmd(0XAF)
    def show(self):
        self.write_cmd(0xb0)
        for page in range(0,64):
            if self.rotate == 0:
                self.column =  63 - page    #set segment remap
            elif self.rotate == 180:
                self.column =  page
                          
            self.write_cmd(0x00 + (self.column & 0x0f))
            self.write_cmd(0x10 + (self.column >> 4))
            for num in range(0,16):
                self.write_data(self.buffer[page*16+num])

def wrap_text(text, max_width):
    """Wrap text to a given width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    # Append the last line if there is any content left
    if current_line:
        lines.append(current_line)

    return lines

def display_text(text, max_width=128):
    """Display wrapped text on the screen."""
    lines = wrap_text(text, max_width // 8)  # Calculate max characters per line
    oled.fill(0)  # Clear display
    y = 0

    for line in lines:
        oled.text(line, 0, y)  # Draw text on the display
        y += 10  # Move to next line (assuming 10-pixel height font)

        # Break if the screen is full
        if y >= oled_height:
            break

    oled.show()  # Update the display

# Initialize the display (SSD1306 with a 128x64 display)
oled_width = 128
oled_height = 64
oled = OLED_1inch3()




#OLED1 = OLED_1inch3()
#OLED1.fill(0x0000) 
#OLED1.show()


def chat_gpt(ssid, password, endpoint, api_key, model, prompt, max_tokens):
        # Just making our internet connection
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        

        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)
        # Handle connection error
        if wlan.status() != 3:
            print(wlan.status())
            raise RuntimeError('network connection failed')
        else:
            print('connected')
            print(wlan.status())
            status = wlan.ifconfig()

        # Begin formatting request
        headers = {'Content-Type': 'application/json',
                   "Authorization": "Bearer " + api_key}
        data = {"model": model,
                "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
                "max_tokens": max_tokens}

        print("Attempting to send Prompt")
        r = urequests.post("https://api.openai.com/v1/{}".format(endpoint),
                           json=data,
                           headers=headers)

        if r.status_code >= 300 or r.status_code < 200:
            print("There was an error with your request \n" +
                  "Response Status: " + str(r.text))
        else:
            print("Success")
            response_data = json.loads(r.text)
            completion = response_data["choices"][0]["message"]["content"]
            #OLED.text(completion)
            #OLED.text(completion,1,2,OLED.white)
            #OLED.show()
            display_text(completion)
            
            print(completion)
        r.close()

chat_gpt(constants.INTERNET_NAME,
         constants.INTERNET_PASSWORD,
         "chat/completions",
         constants.CHAT_GPT_API_KEY,
         "gpt-4o-mini",
         "Tell me my fortune in the style of a chinese fortune cookie.",
         200)
