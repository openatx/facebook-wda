## DESIGN
Create client object

```
import wda


client = wda.Client('http://10.0.0.1:8100')
client.status()

se = client.session('com.example.demo')
se.tap(150, 150) # alias
se.click(150, 150) # alias of tap
se.long_tap(150, 150) # also long_click
se.swipe(50, 60, 70, 80, step=10)

se.screenshot(filename=None) # return PIL object
se(className='Button', text='update').click()
se(text='update').exists # return bool
se(className='Button').count # return number
se(className='EditText').set_text("hello") # input something
se.close()
```

