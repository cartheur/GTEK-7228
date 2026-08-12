## GTEK-7228

Documentation and operation experience

_Background_

Manufactured between 1983 and 

### Interfacing

The Model 7228 is surprisingly easy to interface and there are several methods of handshaking which can be utilized if it is desired to operate at the higher baud rates. The following section describes some of the methods. You can use only the second method with the 7228 version
8.xx.

1. Software handshake. This is perhaps the easiest method of all. When you begin to send data to be programmed, send the first byte but don’t wait for it to be echoed. That would effectively cut
your communication rate in half. Instead, send the second byte, receive the first, send the third byte, receive the second, etc. This technique will allow you to program as fast as the algorithm in use permits. Some devices program faster, some slower! See figure 4.1 for flowchart.

![fig.4.1](/images/fig.4.jpg)

2. CTS/DTR hardware handshaking. The Model 7228 is configured as data terminal equipment, which means that the CTS (clear to send) line is an input to the programmmer which when pulled low
forces the programmer to stop sending. On the other hand, the DTR (data terminal ready) line is an output from the programmer. Version 7.xx DTR will go low when the buffer is about 50% full and
high again when the buffer is about 30% full. Version 8.xx has about the same amount of buffering, but DTR is constantly toggling to obtain the higher baud rates. If you are using hardware hand shake and the DTR line goes low, you should stop sending Immediately to the 7228. The RTS line is pulled high whenever the programmer is plugged in. See Specifications for Cable.

3. Xon/Xoff software handshaking. If you do not monitor the DTR line, the 7228 will transmit an `Xoff` character if there gets to be 9 characters in the FIFO. When the FIFO level drops below 6
characters, an `Xon` will be transmitted. Likewise, when the programmer is sending you data, you may send an XOFF character, which will stop the programmer from sending until it receives an Xon character. `Xon`’s and `Xoff`’s, are not put into the FIFO, but are processed as soon as they are re ceived. Even if you don’t use XON/XOFF handshaking, you will find it useful when using the L, list command, to stop and start the data flow to your screen. `Xon` and `Xoff` are the keyboard equivalents of `control-Q` and `control-S`. Version 8.xx does not send `Xon`/`Xoff`, but will accept it.

4. Please note that the 7228 may communicate at many different baud rates. To initialize to a new baud rate, send a "break" signal to the programmer for more than 100 milliseconds, and then at least 5 milliseconds after you restore from the break, send an `80H` character at the baud rate you wish to begin sending. After that, a space command will cause the prompter to be reissued.