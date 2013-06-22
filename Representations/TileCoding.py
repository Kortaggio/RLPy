"""
Tile Coding Representation

"""


from Tools import *
import numpy as np
from Representation import Representation

class TileCoding(Representation):
    """
    Tile Coding Representation with Hashing Trick
    based on http://incompleteideas.net/rlai.cs.ualberta.ca/RLAI/RLtoolkit/tiles.html
    """

    BIG_INT = 2147483647

    def __init__(self, domain, logger, memory, num_tilings,
                 resolutions=None,
                 resolution_matrix=None,
                 dimensions=None,
                 safety="super",
                 seed=0):
        """

        The TileCoding class can represent several types of tilings at the same
        time. All tilings of one type have the same size of tilings for each state
        dimensions and are only different due to an offset.

        Example: The representation has 2000 dimensions and consists of two
        types of tilings.
        One type covers only dimensions 1 and 2 and has a
        resolution of state_range / 4 and consists of 2 tilings.

        The second type covers dimensions 2, 3 and 4 with resolution state_range / 6 and
        only 1 tiling.
        Such a representation can be created by passing
        >>> memory = 2000
        >>> num_tilings = [2, 1]

        and

        >>> resolutions = [4, 6]
        >>> dimensions = [[1, 2], [2, 3, 4]]

        Instead of resolutions and dimensions, the tilings can also be specified
        by a resolution matrix of dimensions (# types of tilings) x (# state dim.)
        The entry in row i and column j corresponds to the resolution of
        tiling i in dimension j. A resolution < 0 in a dimension maps all possible
        values to the same tile.
        The resolution matrix for the example above is
        >>> resolution_matrix = np.array([[4, 4, 0.5, 0.5], [0.5, 6, 6, 6]],
                                                              dtype="float")

        @param num_tilings: number of tilings; single integer for one type of tiling or
                     a list for several tiling types; see example above.
        @param dimensions: list of list of dimension ids; one list per tiling type
        @param resolutions: list of resolutions; one entry for each type of tilings.
        @param resolution_matrix: see example above
        @param seed: random seed for hashing
        @param memory: size of the "cache", corresponds to number of features
        @param safety: type of collision checking
            either super = detect and avoid all collisions
                   lazy  = faster but may have some false positives
                   none  = don't care about collisions

        """
        self.features_num = memory
        super(TileCoding, self).__init__(domain, logger)
        try:
            self.num_tilings = tuple(num_tilings)
        except TypeError,e:
            self.num_tilings = [num_tilings]
        try:
            self.dimensions = tuple(dimensions)
        except TypeError,e:
            self.dimensions = [dimensions]

        if resolutions is not None:
            try:
                resolutions = tuple(resolutions)
            except TypeError,e:
                resolutions = (resolutions, )

        if resolution_matrix is None:
            # we first need to construct the resolution matrix
            resolution_matrix = np.zeros((len(self.dimensions), self.domain.statespace_limits.shape[0]))
            for i,s in enumerate(self.dimensions):
                for d in s:
                    res[i,d] = resolutions[i]
        self.scaling_matrix = (self.domain.statespace_limits[:,1] - self.domain.statespace_limits[:,0]) / resolution_matrix

        # now only hashing stuff
        self.seed=seed
        self.safety = safety
        if safety == "super":
            size = self.domain.state_space_dims+1
        elif safety == "lazy":
            size = 1
        else:
            size = 0
        self.check_data = -np.ones((self.features_num, size), dtype=np.int)
        self.counts = np.zeros((self.features_num), dtype=np.long)
        self.collisions = 0
        self.R = np.random.RandomState(seed).randint(self.BIG_INT / 4  ,size=self.features_num)

    def phi_nonTerminal(self, s):

        phi = np.zeros((self.features_num))
        sn = np.empty((len(s)+1), dtype="int")
        for e, n_t in enumerate(self.num_tilings):
            sn[0] = e # first dimension is used to avoid collisions between different tilings
            sn[1:] = (s - self.domain.statespace_limits[:,0]) / self.scaling_matrix[e]
            for i in range(n_t):
                # compute "virtual" address
                A = sn - np.mod(sn - i, n_t)
                # compute "physical" address
                j = self._physical_addr(A)
                phi[j] = 1
        return phi


    def _hash(self, A, increment=449, max=None):
        """
        hashing without collision detection
        """
        # TODO implement in cython if speed needs to be improved
        max = self.features_num if max == None else max
        return int(self.R[np.mod(A + np.arange(len(A))*increment, self.features_num)].sum()) % max

    def _physical_addr(self, A):
        """
        Map a virtual vector address A to a physical address i.e. the actual
        feature number.
        This is the actual hashing trick
        """
        h1 = self._hash(A)
        if self.safety == "super":
            # use full value to detect collisions
            check_val = A
        else:
            # use second hash
            check_val = self._bash(A, increment = 457, max = self.BIG_INT)

        if self.counts[h1] == 0:
            # first time, set up data
            self.check_data[h1] = check_val
            self.counts[h1] += 1
            return h1
        elif np.all(check_val == self.check_data[h1]):
            # clear hit, everything's fine
            self.counts[h1] += 1
            return h1
        elif self.safety == "none":
            self.collisions += 1
            return h1
        else:
            h2 = 1 + 2 * self._hash(A, max = self.BIG_INT / 4)
            for i in xrange(self.features_num):
                h1 = (h1 + h2) % self.features_num
                if self.counts[h1] == 0 or np.all(self.check_data[h1] == check_val):
                    self.check_data[h1] = check_val
                    self.counts[h1] += 1
                    return h1
            self.collisions += 1
            self.logger.log("Tile memory too small")
            return h1




if __name__ == "__main__":
    from Domains.acrobot_back import Acrobot
    domain = Acrobot(None)
    resolution_mat = .5 * np.ones((2,4))
    tile_matrix = array(mat("""
    48 48 48 48;
    1 18 18 18; 18 1 18 18; 18 18 1 18; 18 18 18 1;
    1 1 12 12; 1 12 12 1; 1 12 1 12; 12 1 1 12; 12 1 12 1; 12 12 1 1;
    1 1 1 18; 1 1 18 1; 1 18 1 1; 18 1 1 1"""), dtype="float")
    resolution_mat = tile_matrix
    resolution_mat[resolution_mat == 1] = 0.5
    t = TileCoding(num_tilings=[12, 3, 3, 3, 3]+[2]*6+[3]*4, memory=2000, logger=Logger(),
                   domain=domain, resolution_matrix=resolution_mat)
    for i in np.linspace(-1, 1, 20):
        print i
        a = np.nonzero(t.phi_nonTerminal(np.array([np.pi*i,0.,0.,0.])))[0]
        sort(a)
        print a

