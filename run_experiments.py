if start_at_current_position:
    chip.start_at_device(current_dev, run_skipped_devices)  # sort the chip devices list to start at the current device (and either skip the devices or add them to the end of the list)

# loop over all devices that were loaded by the user
cont = True
for dev in chip:
    # run the experiments that were loaded by the user
    for experiment in chip.experiments:
        if dev in experiment:  # if the experiment should be run on the current device:
            check_user_input()  # check for user input (asynchronously)
            # move the cascade to the new device position. The class checks if it is already at the current position and moves only when it needs to
            cascade.move_abs(chip.get_device_position(dev))
            check_user_input()  # check for user input (asynchronously)
            # correct the signal switch settings hp / adwin
            settings = experiment.get_switch_settings()
            if not settings:
                settings = signal_switch.load_settings(experiment.script)  # load the signal switch settings
            signal_switch.route_settings(settings)
            # run the experiment
            output = experiment.run(dev)
            # handle experiment outputs
            if exp_stop_code in output:
                cont = False
                break
            if exp_skip_code in output:
                break
            while exp_run_code in output:
                # running extra experiments if required
                index = output.index(exp_run_code)
                try:
                    script = output[index+1]
                    device = output[index+2]
                except:
                    pass
                if not device or not re.match('([a-zA-Z]+)([0-9]+)',device):
                    device = dev
                if not script:
                    break
                exp = Experiment(script, name, device)
                check_user_input()  # check for user input (asynchronously)
                cascade.move_abs(chip.get_device_position(device))
                check_user_input()  # check for user input (asynchronously)
                output = exp.run(device)

    if not cont:
        break

# route the switch back to adwin for other people.
signal_switch.route(1,'ADWIN')
signal_switch.route(2,'ADWIN')
signal_switch.route(3,'ADWIN')

if return_to_start:
    cascade.move_abs(chip.get_device_position(chip.devices[0])) #move back to the front
#cascade.up()  # put the probes up, so that we see the measurement is completed.

for experiment in chip.experiments:
    experiment.end()