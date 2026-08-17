# Feeling The (ROM) Burn

Subtitle: a short podcast script about reviving a dusty GTEK 7228 on a modern Debian bench

Date: 17 August 2026

## Episode format

- Solo host
- 8 to 12 minutes
- Quiet bench ambience, fan noise, gentle relay clicks, tool sounds
- Tone: warm, reflective, nerdy, lightly cinematic

## Episode summary

This episode tells the story of getting ready to revive an old GTEK 7228 ROM programmer that has likely been sitting unused for years after a life in a Tektronix shop. The emotional center is not just retro hardware nostalgia, but the physical ritual of bring-up: dust, connectors, manuals, serial cabling, and the strange anticipation of waiting for a machine to speak again.

## Cold open

There is a certain kind of silence that only old bench equipment has.

Not the silence of something modern and powered down. Not sleep mode. Not standby. I mean the silence of a machine that has been offline for years, sitting somewhere under dust, carrying a whole working life inside it, and no promise at all that it will ever wake up cleanly again.

On the bench today: a GTEK 7228. A ROM programmer from the era when programming a chip felt like an industrial act. Metal, switches, sockets, serial cables, manuals, and patience.

And before we even turn it on, we have to do the first honest thing any old machine asks of us:

open it, clean it, and see what time left behind.

## Intro

Welcome to Feeling The ROM Burn.

This is a short field note from the bench: part restoration diary, part bring-up log, part love letter to tools that were built to do one job well and then just kept doing it for decades.

Today’s machine is a GTEK 7228, and the goal is simple on paper:

get it talking to a modern Debian box over serial.

But of course, that sentence hides the real story.

Because before there is a prompt, before there is a successful command, before there is any satisfying little rhythm of bytes crossing a cable, there is the long pause where you ask:

what exactly is still alive in here?

## Segment 1: The object itself

The 7228 has history in it.

It likely spent time in a Tektronix shop. That alone gives it a kind of emotional weight. You can imagine it sitting on a bench near scopes, logic probes, antistatic mats, tiny labeled parts drawers, and coffee that went cold two hours earlier because someone was chasing a fault line through a board.

These machines were practical tools, but they also carried a kind of ceremony. You did not just click "flash." You selected a device, verified formats, watched handshaking, cared about cable pinout, and paid attention to what the machine was telling you.

That’s part of what makes reviving one now so satisfying.

It asks you to slow down.

## Segment 2: Dust first, power later

There is always a temptation with old hardware to jump straight to power.

Don’t.

Especially not with something that has been sitting for years.

The first stage of bring-up is not electrical. It is archaeological.

Open the case.
Photograph everything before touching it.
Look for dust mats, corrosion, cracked insulation, old repair work, loose connectors, tired capacitors, anything that says this machine’s last chapter was messier than its first one.

And there is something intimate about this part. The machine is not "running" yet, but it is already telling you things. The dirt patterns tell you airflow. The connector oxidation tells you storage conditions. The board color tells you heat history. A missing screw tells you someone was in here before you.

This is where restoration stops being abstract.

You are not dealing with a model number. You are dealing with a life.

## Segment 3: Modern host, old protocol

On the modern side, the setup is almost comically elegant by comparison.

A Debian box.
An Eminent EM1016 USB-to-RS232 adapter.
A PL2303 serial device that appears as a nice clean `/dev/serial/by-id/...` path.
A Tcl/Tk terminal script adapted just for this repo.

That is the bridge between 2026 and a machine designed for a much earlier world.

And that bridge matters, because a lot of the work here is not heroic reverse engineering. It is respecting interfaces.

The 7228 wants RS-232, not TTL.
It wants a real serial path.
It wants the right baud rate.
It wants sane handshaking.
It wants you to listen when it says "slow down."

There is a kind of beauty in that.

## Segment 4: Handshake as personality

One of my favorite details in this whole bring-up story is the handshake.

Modern people hear "serial" and imagine a dumb stream of bytes.

But the 7228 is not dumb. It has opinions.

It can use XON and XOFF. It can use CTS and DTR. It can tell you, in effect:

I am ready.
I am not ready.
Pause.
Resume.
Do not flood me.

That is not just protocol. That is temperament.

And I love that the current plan is to begin with the simplest, most respectful approach:

three wires, software flow control first, hardware handshake later only if needed.

Not because complicated is bad.

Because first contact should be calm.

## Segment 5: The moment we are aiming for

The real target is tiny.

Not a full production workflow.
Not a triumphant montage.
Not even a successful chip burn, at least not yet.

The target is a first sign of life.

A readable line.
A prompt.
An echoed character.
Something that proves the cable is right, the adapter is right, the port is right, the machine is awake, and the years of silence are over.

That moment is small if you describe it technically.

But emotionally, that moment is enormous.

It means the machine did not vanish into history.
It means the interface still exists.
It means the knowledge embedded in this thing can still be touched.

## Closing

So that is where we are.

The docs are in place.
The adapter path is simplified.
The cable pinout is mapped.
The Tcl/Tk terminal is ready.
The baud list is constrained to what the GTEK documentation actually supports.
And the next real step is physical:

open the unit,
clean the years off it,
inspect it honestly,
and only then let it try to speak.

This has been Feeling The ROM Burn.

Not every restoration starts with power.
Sometimes it starts with dust, patience, and a serial cable made with care.

And if all goes well, next time, the 7228 answers back.

## Optional outro tag

Bench notes continue in this repo.

If you know the sound of old equipment waking up, you already know why this matters.

## Recording notes

- Read the cold open slowly.
- Leave short pauses after lines like "what exactly is still alive in here?"
- Add subtle bench ambience, not dramatic music.
- If recorded, keep the vocal delivery intimate rather than theatrical.
