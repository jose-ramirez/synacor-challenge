class Utils:

    @staticmethod
    def to_int(byte_array):
        lo, hi = byte_array[1], byte_array[0]
        return 256 * int(lo) + int(hi)