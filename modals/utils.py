def find_available(time_hp, time_tkb):
    non_coincidence = {}

    for dk_class, dk_schedule in time_hp.items():
        is_fully_coinciding = False  # Flag to check if any date-period coincides
        
        for date, dk_periods in dk_schedule.items():
            for tkb_class, tkb_schedule in time_tkb.items():
                if date in tkb_schedule:
                    # Check for any overlap in periods
                    if any(period in dk_periods for period in tkb_schedule[date]):
                        is_fully_coinciding = True
                        break
            if is_fully_coinciding:
                break

        # If no date-period coincides for the entire item, add it to the result
        if not is_fully_coinciding:
            non_coincidence[dk_class] = dk_schedule

    return non_coincidence