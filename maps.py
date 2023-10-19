from edcmap import Map

with open("CURRENT.bin", mode="rb") as bin:
    soi = Map(
        file=bin,
        config={
            "start": 0x78F94,
            "fun": lambda x: x * -0.023437 + 78,
            "x": 0x78F56,
            "x_fun": lambda x: x,
            "y": 0x78F7A,
            "y_fun": lambda x: x * 0.01,
        },
    )

    selector = Map(
        file=bin,
        config={
            "start": 0x7A1F6,
            "fun": lambda x: round(x / 256, 0),
            "x": 0x7A1EA,
            "x_fun": lambda x: x * -0.023437 + 78,
        },
    )

    durations = [
        Map(
            file=bin,
            config={
                "start": 0x7946A,
                "fun": lambda x: x * 0.023437,
                "x": 0x7943E,
                "x_fun": lambda x: x * 0.01,
                "y": 0x79456,
                "y_fun": lambda x: x,
            },
        ),
        Map(
            file=bin,
            config={
                "start": 0x7957E,
                "fun": lambda x: x * 0.023437,
                "x": 0x79536,
                "x_fun": lambda x: x * 0.01,
                "y": 0x79558,
                "y_fun": lambda x: x,
            },
        ),
        Map(
            file=bin,
            config={
                "start": 0x79804,
                "fun": lambda x: x * 0.023437,
                "x": 0x797BC,
                "x_fun": lambda x: x * 0.01,
                "y": 0x797DE,
                "y_fun": lambda x: x,
            },
        ),
        Map(
            file=bin,
            config={
                "start": 0x79A8A,
                "fun": lambda x: x * 0.023437,
                "x": 0x79A42,
                "x_fun": lambda x: x * 0.01,
                "y": 0x79A64,
                "y_fun": lambda x: x,
            },
        ),
        Map(
            file=bin,
            config={
                "start": 0x79D10,
                "fun": lambda x: x * 0.023437,
                "x": 0x79CC8,
                "x_fun": lambda x: x * 0.01,
                "y": 0x79CEA,
                "y_fun": lambda x: x,
            },
        ),
        Map(
            file=bin,
            config={
                "start": 0x79F78,
                "fun": lambda x: x * 0.023437,
                "x": 0x79F4E,
                "x_fun": lambda x: x * 0.01,
                "y": 0x79F64,
                "y_fun": lambda x: x,
            },
        ),
    ]
