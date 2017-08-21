os.chdir(qtlab_dir)

# load the cascade instrument
cascade = Cascade()

print("Please make sure that the cascade probes are in the contact setting!")
# try to find the current position of the cascade from the file.
if not cascade.store_position_file(filename='%s/positioning/%s.dat' % (script_dir, name)) or not load_saved_position:
    # current position not found, ask the user for the current position of the cascade
    cont = False
    while not cont:
        try:
            current_dev = raw_input('Current device (%s)? ' % dev)
            if not current_dev:
                current_dev = dev
        except:
            current_dev = raw_input('Current device? ')
        pos = chip.get_device_position(current_dev)
        if pos[0] == -1 and pos[1] == -1:
            print("Please input a device that is on the chip.")
        else:
            cont = True
    cascade.position = chip.get_device_position(current_dev)

# get the current device from the cascade position
current_dev = chip.get_device_from_position(cascade.position)

if probe_contact_safety:
    n = raw_input("Press enter if the probes are in the contact setting...")
    # if the user inputs anything, quit the application before continuing.
    if n:
        raise SystemExit()
cascade.down()  #put the probes down. Ideally, you'd check if they were safe before starting, but it doesnt look like the cascade supports this.