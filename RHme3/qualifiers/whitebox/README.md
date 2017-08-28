# Challenge 1: Whitebox

## DCA
This challenge can be solved easily with DCA using the
[SideChannelMarvels](https://github.com/SideChannelMarvels) tools.

Follow the instructions at https://github.com/SideChannelMarvels/Orka to build
the SideChannelMarvels Docker container.

Start the container with
```bash
 $ docker run -v $(pwd):/workdir --privileged -it scamarvels
```
and then run the attack from inside the container:
```bash
 # cd /workdir
 # python trace_it.py
 [...]
 # daredevil -c mem_addr1_rw1_100_42808.attack_sbox.config
 [...]
```

See `daredevil.log` for full log output.

The flag is
```
 $ echo -n '61316c5f7434623133355f525f6f5235' | xxd -r -p
a1l_t4b135_R_oR5
```