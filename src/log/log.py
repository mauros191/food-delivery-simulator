import config.config as config


# Config log for testing
LOG = []
CHECK_RIDERS: bool = True if len(config.LOG_ONLY_RIDERS) > 0 else False
CHECK_ORDERS: bool = True if len(config.LOG_ONLY_ORDERS) > 0 else False


# Show all logs after simulation
def show_after_simulation():
    if not config.LOG_REAL_TIME:
        for m in LOG:
            show(m)


# Save message log
def save(msg: str) -> None:
    LOG.append(msg)


# Show log
def show(msg: str) -> None:
    if not CHECK_ORDERS and not CHECK_RIDERS:
        print(msg)

    else:
        split_msg = msg.split(" ")

        # Get type_msg (colors issue)
        if len(split_msg[1]) == 10:
            type_msg = split_msg[1][5:]
        else:
            type_msg = split_msg[1]

        # Log only order in ORDERS if CHECK_ORDERS is true
        if type_msg == "ORDER":
            if CHECK_ORDERS:
                if int(split_msg[2]) in config.LOG_ONLY_ORDERS:
                    print(msg)
            else:
                print(msg)

        # Log only order in ORDERS if CHECK_ORDERS is true
        elif type_msg == "RIDER":
            if CHECK_RIDERS:
                if int(split_msg[2]) in config.LOG_ONLY_RIDERS:
                    print(msg)
            else:
                print(msg)
