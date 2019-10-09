

# Expect marriages to only ever contain items of type Marriage
class Marriages(dict):

    # Return unplayed marriage or None if not applicable
    def unplayed_marriage(self):

        for i, marriage in self.items():
            if marriage.declared_but_not_played:
                return marriage
        return None

    # Search all marriages and return the total of the unawarded marriages
    def award_points(self, player):
        return_points = 0
        for i, marriage in self.items():
            if not marriage.points_awarded and player is marriage.player:
                return_points += marriage.points
                marriage.points_awarded = True

        return return_points
