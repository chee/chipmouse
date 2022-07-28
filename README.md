
# Table of Contents

1.  [chipmouse](#orgcb93687)
    1.  [Setup](#org2c313b2)
    2.  [notes](#org65b2c8d)
    3.  [hoo-hoo](#org094d934)
    4.  [service files](#org0c3786a)
        1.  [~/.config/systemd/user/CHIPMOUSE.service](#orga9305f2)
        2.  [~/.config/systemd/user/a2jmidid.service](#orgc4e065d)
        3.  [~/.config/systemd/user/jackd.service](#org2218b01)


<a id="orgcb93687"></a>

# chipmouse

Requirements:

-   raspberry pi zero wh
-   pirate audio headphone amp
-   op-1
-   a running jack2 server
-   adlrt
-   espeak
-   the op-1 disk needs to automount to `~/op-1/disk`. TODO add instructions for this with udisks2 and a symlink


<a id="org2c313b2"></a>

## Setup

1.  install arch linux on your rapsberry pi microsd <https://archlinuxarm.org/platforms/armv6/raspberry-pi>


<a id="org65b2c8d"></a>

## notes

highly recommend swithing to COM mode and switching to OPT and turning off >-[X]-> so it doesn't draw too much electric


<a id="org094d934"></a>

## hoo-hoo

![img](./assets/menu1.gif "an early gif of menu action")


<a id="org0c3786a"></a>

## service files


<a id="orga9305f2"></a>

### ~/.config/systemd/user/CHIPMOUSE.service

```systemd
[Unit]
Description=CHIPMOUSE
After=jackd.service

[Service]
Type=simple
WorkingDirectory=/home/alarm/chipmouse
Environment="TERM=xterm"
ExecStart=sh -c 'python -m chipmouse -m pi'
Restart=always

[Install]
WantedBy=default.target
```

<a id="orgc4e065d"></a>

### ~/.config/systemd/user/a2jmidid.service

```systemd
[Unit]
Description=alsa to jack midi bridge daemon
After=jackd.service

[Install]
WantedBy=default.target

[Service]
Type=simple
ExecStart=/bin/a2jmidid -e
```

<a id="org2218b01"></a>

### ~/.config/systemd/user/jackd.service

```systemd
[Unit]
Description=Jack audio server
After=sound.target

[Install]
WantedBy=default.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/jackd -d alsa -r 24000 -p 256 -n 2
```
