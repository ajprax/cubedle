import math


class Glicko2:
    """
    Implementation of the Glicko-2 rating system
    Based on the algorithm described at http://www.glicko.net/glicko/glicko2.pdf
    """
    
    # System constant - typically between 0.3 and 1.2
    TAU = 0.5
    
    @staticmethod
    def scale_down(rating):
        """Convert rating to Glicko-2 scale (μ)"""
        return (rating - 1500) / 173.7178
    
    @staticmethod
    def scale_up(mu):
        """Convert from Glicko-2 scale back to rating"""
        return 173.7178 * mu + 1500
    
    @staticmethod
    def scale_rd_down(rd):
        """Convert RD to Glicko-2 scale (φ)"""
        return rd / 173.7178
    
    @staticmethod
    def scale_rd_up(phi):
        """Convert from Glicko-2 RD scale back to RD"""
        return 173.7178 * phi
    
    @staticmethod
    def g(phi):
        """g(φ) function from Glicko-2"""
        return 1 / math.sqrt(1 + 3 * phi**2 / math.pi**2)
    
    @staticmethod
    def E(mu, mu_j, phi_j):
        """Expected outcome function E(μ, μⱼ, φⱼ)"""
        return 1 / (1 + math.exp(-Glicko2.g(phi_j) * (mu - mu_j)))
    
    @staticmethod
    def update_ratings(player1_rating, player1_rd, player1_vol,
                      player2_rating, player2_rd, player2_vol,
                      outcome):
        """
        Update ratings for two players after a match.
        
        Args:
            player1_rating: Player 1's current rating
            player1_rd: Player 1's current rating deviation
            player1_vol: Player 1's current volatility
            player2_rating: Player 2's current rating
            player2_rd: Player 2's current rating deviation
            player2_vol: Player 2's current volatility
            outcome: Result for player 1 (1.0 for win, 0.5 for draw, 0.0 for loss)
        
        Returns:
            tuple: (new_p1_rating, new_p1_rd, new_p1_vol, new_p2_rating, new_p2_rd, new_p2_vol)
        """
        
        # Convert to Glicko-2 scale
        mu1 = Glicko2.scale_down(player1_rating)
        phi1 = Glicko2.scale_rd_down(player1_rd)
        sigma1 = player1_vol
        
        mu2 = Glicko2.scale_down(player2_rating)
        phi2 = Glicko2.scale_rd_down(player2_rd)
        sigma2 = player2_vol
        
        # Update player 1
        new_mu1, new_phi1, new_sigma1 = Glicko2._update_single_player(
            mu1, phi1, sigma1, [(mu2, phi2, outcome)]
        )
        
        # Update player 2 (with inverted outcome)
        new_mu2, new_phi2, new_sigma2 = Glicko2._update_single_player(
            mu2, phi2, sigma2, [(mu1, phi1, 1.0 - outcome)]
        )
        
        # Convert back to original scale
        new_p1_rating = Glicko2.scale_up(new_mu1)
        new_p1_rd = Glicko2.scale_rd_up(new_phi1)
        
        new_p2_rating = Glicko2.scale_up(new_mu2)
        new_p2_rd = Glicko2.scale_rd_up(new_phi2)
        
        return (new_p1_rating, new_p1_rd, new_sigma1,
                new_p2_rating, new_p2_rd, new_sigma2)
    
    @staticmethod
    def _update_single_player(mu, phi, sigma, results):
        """
        Update a single player's rating given their match results.
        
        Args:
            mu: Player's rating (Glicko-2 scale)
            phi: Player's RD (Glicko-2 scale)
            sigma: Player's volatility
            results: List of (opponent_mu, opponent_phi, outcome) tuples
        
        Returns:
            tuple: (new_mu, new_phi, new_sigma)
        """
        
        if not results:
            # If no games played, just increase RD due to time
            new_phi = math.sqrt(phi**2 + sigma**2)
            return mu, new_phi, sigma
        
        # Step 2: Compute v
        v = 0
        for opp_mu, opp_phi, _ in results:
            g_opp_phi = Glicko2.g(opp_phi)
            E_outcome = Glicko2.E(mu, opp_mu, opp_phi)
            v += g_opp_phi**2 * E_outcome * (1 - E_outcome)
        v = 1 / v
        
        # Step 3: Compute delta
        delta = 0
        for opp_mu, opp_phi, outcome in results:
            g_opp_phi = Glicko2.g(opp_phi)
            E_outcome = Glicko2.E(mu, opp_mu, opp_phi)
            delta += g_opp_phi * (outcome - E_outcome)
        delta *= v
        
        # Step 4: Compute new volatility
        new_sigma = Glicko2._compute_new_volatility(phi, sigma, delta, v)
        
        # Step 5: Update phi and mu
        phi_star = math.sqrt(phi**2 + new_sigma**2)
        new_phi = 1 / math.sqrt(1 / phi_star**2 + 1 / v)
        new_mu = mu + new_phi**2 * sum(
            Glicko2.g(opp_phi) * (outcome - Glicko2.E(mu, opp_mu, opp_phi))
            for opp_mu, opp_phi, outcome in results
        )
        
        return new_mu, new_phi, new_sigma
    
    @staticmethod
    def _compute_new_volatility(phi, sigma, delta, v):
        """Compute new volatility using Illinois algorithm"""
        
        phi2 = phi**2
        delta2 = delta**2
        tau2 = Glicko2.TAU**2
        
        def f(x):
            ex = math.exp(x)
            return (ex * (delta2 - phi2 - v - ex) / (2 * (phi2 + v + ex)**2) - 
                    (x - math.log(sigma**2)) / tau2)
        
        # Initial bounds
        A = math.log(sigma**2)
        if delta2 > phi2 + v:
            B = math.log(delta2 - phi2 - v)
        else:
            k = 1
            while f(A - k * Glicko2.TAU) < 0:
                k += 1
            B = A - k * Glicko2.TAU
        
        # Illinois algorithm
        fa = f(A)
        fb = f(B)
        
        epsilon = 0.000001
        while abs(B - A) > epsilon:
            C = A + (A - B) * fa / (fb - fa)
            fc = f(C)
            
            if fc * fb <= 0:
                A = B
                fa = fb
            else:
                fa = fa / 2
            
            B = C
            fb = fc
        
        return math.exp(A / 2)