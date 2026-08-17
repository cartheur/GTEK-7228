## GTEK-7228

The “GTEK 7228” is a vintage EPROM/ROM programmer—i.e., a bench device used by hobbyists/technicians to program erasable memory chips in the pre-flash era - such as 27C-series EPROMs. It’s typically operated over a serial connection using a simple command/menu interface, where you select the EPROM type/device from a prompt and then send read/write commands in standard text formats like Intel HEX or Motorola S-Record.

_Background_

Manufactured between 1983 and 1997, one of the best ROM writers/readers that have _ever_ been made. The company bio is:

```
Over 28 years of leadership providing solutions for Industrial Electronics and Communications Hardware and Software Development, Worldwide.

KATRINA NOTICE - Gtek and its facility were severely damaged by Hurricane Katrina on 29 August 2005. As of 1 February 2010, no manufacturing has taken place since Katrina, nor is any expected to in the future. 
```
Documentation and operation experience - here lies my journey. The comms are silent.

Additional serial adapter and USB-TTL wiring guidance is in [docs/serial-adapter-guide.md](docs/serial-adapter-guide.md). For the current experimental setup, the documented `USB-to-TTL UART -> MAX232 -> GTEK 7228` path is the intended hardware approach.

For first-time diagnosis and serial bring-up on a modern Debian machine, start with [docs/first-bringup-debian.md](docs/first-bringup-debian.md). That guide uses the local helper scripts in `scripts/` and is the quickest path to first contact with a dusty unit.

If you need to fabricate the physical link first, use [docs/cable-build.md](docs/cable-build.md) for the shortest cable path and exact first-pass pinout.

![7228](/images/7228-1-mini.jpg)

### Interfacing

The Model 7228 is surprisingly easy to interface and there are several methods of handshaking which can be utilized if it is desired to operate at the higher baud rates. The following section describes some of the methods. You can use only the second method with the 7228 version
8.xx.

1. Software handshake. This is perhaps the easiest method of all. When you begin to send data to be programmed, send the first byte but don’t wait for it to be echoed. That would effectively cut
your communication rate in half. Instead, send the second byte, receive the first, send the third byte, receive the second, etc. This technique will allow you to program as fast as the algorithm in use permits. Some devices program faster, some slower! See figure 4.1 for flowchart.

![fig.4.1](/images/fig.4-mini.jpg)

2. CTS/DTR hardware handshaking. The Model 7228 is configured as data terminal equipment, which means that the CTS (clear to send) line is an input to the programmmer which when pulled low
forces the programmer to stop sending. On the other hand, the DTR (data terminal ready) line is an output from the programmer. Version 7.xx DTR will go low when the buffer is about 50% full and
high again when the buffer is about 30% full. Version 8.xx has about the same amount of buffering, but DTR is constantly toggling to obtain the higher baud rates. If you are using hardware hand shake and the DTR line goes low, you should stop sending Immediately to the 7228. The RTS line is pulled high whenever the programmer is plugged in. See Specifications for Cable.

3. Xon/Xoff software handshaking. If you do not monitor the DTR line, the 7228 will transmit an `Xoff` character if there gets to be 9 characters in the FIFO. When the FIFO level drops below 6
characters, an `Xon` will be transmitted. Likewise, when the programmer is sending you data, you may send an XOFF character, which will stop the programmer from sending until it receives an Xon character. `Xon`’s and `Xoff`’s, are not put into the FIFO, but are processed as soon as they are re ceived. Even if you don’t use XON/XOFF handshaking, you will find it useful when using the L, list command, to stop and start the data flow to your screen. `Xon` and `Xoff` are the keyboard equivalents of `control-Q` and `control-S`. Version 8.xx does not send `Xon`/`Xoff`, but will accept it.

4. Please note that the 7228 may communicate at many different baud rates. To initialize to a new baud rate, send a "break" signal to the programmer for more than 100 milliseconds, and then at least 5 milliseconds after you restore from the break, send an `80H` character at the baud rate you wish to begin sending. After that, a space command will cause the prompter to be reissued.

### Programmer Interface

The model 7228 has a DB25P connector configured as Data Terminal Equipment (DTE).

Pin# Direction Function

| Pin | Signal | Direction | Function / Notes |
| --- | --- | --- | --- |
| 1 | EG | <--> | Equipment Ground |
| 2 | TXD | --> | Transmit Data |
| 3 | RXD | <-- | Receive Data |
| 4 | RTS | --> | Request To Send. Always active when power is on. |
| 5 | CTS | <-- | Clear To Send. High enables 7228 to transmit data. Pulled high internally. |
| 6 | DSR | <-- | Data Set Ready. Not used. |
| 7 | SG | <--> | Signal Ground |
| 20 | DTR | --> | Data Terminal Ready. High when programmer willing to accept data. |

### Making the cable

AT DB9 (male) to 7228 DB25 (female)
| AT Signal | AT Pin | 7228 Pin | 7228 Signal |
| --- | --- | --- | --- |
| CD | 1 | 8 | CD |
| RXD | 2 | 2 | TXD |
| TXD | 3 | 3 | RXD |
| DTR | 4 | 5 | CTS |
| SG | 5 | 7 | SG |
| DSR | 6 | 4 | RTS |
| RTS | 7 | 6 | DSR |
| CTS | 8 | 20 | DTR |
| RD | 9 | NC | NC |

#### Cold links

ftp://ftp.gtek.com/pub/linux/linux.tar.gz
