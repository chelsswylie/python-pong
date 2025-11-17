class PongDTO:
    """This is a data transfer object containing the variables that will be passed between server and clients."""

    # Initiate to default values
    def __init__(self):
        self.game_id = 0
        self.player_id = 0
        self.player_x = []
        self.player_y = []
        self.ball_x = 0
        self.ball_y = 0
        self.ball_velocity_x = 0
        self.ball_velocity_y = 0
        self.ball_direction_x = ''
        self.ball_direction_y = ''
        self.start_play = False
        self.msg = ''
        self.end_play = False
        self.points = [0, 0]