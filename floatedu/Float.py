
__all__ = (
    "Float16", "BFloat16", "Float32", "Float64", "Float128",
)


class Float(list):
    def __init__(f, binary_str):
        if type(f) == Float:
            # It's supposed to be subclassed and have k, p, and
            # bias values set.
            raise RuntimeError("Not supposed to be used directly")

        super().__init__(f)

        # Strip spaces and underscores
        bits = binary_str.replace(" ", "").replace("_", "")

        # Partition bits according to k and p values
        parts = _int_partitions(bits, 1, f.k, f.p - 1)
        f.extend(parts)

    @property
    def sign_bit(f): return f[0]

    @property
    def exponent_bits(f): return f[1]

    @property
    def fraction_bits(f): return f[2]

    sign_bit.__doc__ = exponent_bits.__doc__ = fraction_bits.__doc__ = (
        """
        Return the bits as a list.

        Changes to the list will change the value of the float.

        E.g:

            num = Float16("0" * 16)  # num.value: 0.0
            num.sign_bit[0] = 1      # num.value: -0.0

        """
    )

    @property
    def kind(f):
        """
        Return the type of float.

        The types are:
            "normal", "subnormal", "zero", "infinity", "nan".
        """
        if all(f.exponent_bits):  # all bits set to 1
            if any(f.fraction_bits):  # some bits set to 1
                return "nan"
            else:
                return "infinity"

        if not any(f.exponent_bits):  # all bits set to 0
            if any(f.fraction_bits):  # some bits set to 1
                return "subnormal"
            else:
                return "zero"

        return "normal"

    @property
    def value(f):
        """
        Return the value of the float.

        The value is a native python float. This means that if the
        number is too large or too small for the native implementation
        it can't be trusted.
        """
        # Choose float's algorithm or value as per specs
        kind = f.kind
        if kind == "zero":
            return f.sign * 0.0
        elif kind == "infinity":
            return f.sign * float("inf")
        elif kind == "nan":
            return float("nan")
        elif kind == "subnormal":
            significand = 0.0 + f.fraction
            return f.sign * 2**-(f.bias - 1) * significand
        elif kind == "normal":
            significand = 1.0 + f.fraction
            return f.sign * 2**(f.exponent - f.bias) * significand

        raise NotImplementedError("Unknown float type")

    @property
    def sign(f):
        """
        Return the sign.

        The sign bit is the exponent of -1:
        (-1)^bit
        """
        return (-1)**f.sign_bit[0]

    @property
    def exponent(f):
        """
        Return the exponent as an integer.

        Convert the bits of the exponent part as if they are an
        unsigned integer:
        2^0 * bit_1 + 2^1 * bit_2 + 2^3 * bit_3 + ...
        """
        #  exponent = int("".join(map(str, f.exponent_bits)), 2)
        exponent = 0
        for bit, n in zip(f.exponent_bits, range(f.k)[::-1]):  # k..0
            if bit:
                exponent += 2**n
        return exponent

    @property
    def fraction(f):
        """
        Return the fraction as a float.

        Reading from left-to-right the bits in the fraction part, the
        equation is:
        bit_n * 2^-1 + bit_{n-1} * 2^-2 + bit_{n-2} * 2^-3 + ...
        """
        fraction = 0.0
        for bit, n in zip(f.fraction_bits, range(1, f.p)):  # 1..(p-1)
            if bit:
                fraction += 2**-n
        return fraction

    @property
    def significand(f):
        """Return the significand (*redundant)."""
        if f.kind == "subnormal":
            return 0 + f.fraction
        if f.kind == "normal":
            return 1 + f.fraction
        else:
            return None

    @property
    def str_bits(f):
        """Return readable representation of the bits as a string."""
        return "{}_{}_{}".format(
            f.sign_bit[0],
            "".join(map(str, f.exponent_bits)),
            "".join(map(str, f.fraction_bits)),
        )

    @property
    def as_dict(f):
        """Return a dict with all the properties of the float."""
        return {
            k: getattr(f, k)
            for k in (
                "value", "kind", "k", "p", "bias", "str_bits", "sign",
                "exponent", "fraction", "significand"
            )
        }

    def __repr__(f):
        return (
            f"{{'value': float('{f.value}'),\n"
            f" 'kind': '{f.kind}', 'k': {f.k}, 'p': {f.p}, "
            f"'bias': {f.bias},\n"
            f" 'bits': '{f.str_bits}',\n"
            f" 'sign': {f.sign}, 'exponent': {f.exponent}, "
            f"'fraction': {f.fraction},\n"
            f" 'significand': {f.significand},\n"
            f"}}"
        )

    def __str__(f):
        return f"{f.value}"


# Create the various float types according to the IEEE 754
class Float16(Float):  (k, p, bias) = 5,  11,  15
class BFloat16(Float): (k, p, bias) = 8,  8,   127
class Float32(Float):  (k, p, bias) = 8,  24,  127
class Float64(Float):  (k, p, bias) = 11, 53,  1023
class Float128(Float): (k, p, bias) = 15, 113, 16383
class Float256(Float): (k, p, bias) = 19, 237, 262143


def _int_partitions(s, *lengths):
    """
    Create a generator to partition and convert a string.

    The string `s' is split according to `lengths' and every part
    is converted to a list on integers.
    """
    end = 0
    for length in lengths:
        start, end = end, end + length
        yield list(map(int, s[start:end]))


def new_float_class(name, n_exponent, n_significand, exponent_bias):
    """
    Return new class which is a subclass of `Float' and initialize
    p, k, and bias values.

    :param name internal name of the newly created class
    :param n_exponent (k) number of bits of the exponent
    :param n_significand (p) number of bits (implicit one included)
        of the significand
    :param exponent_bias (bias) exponent bias
    """
    class CustomFloat(Float):
        k, p, bias, = n_exponent, n_significand, exponent_bias
        __qualname__ = __name__ = name
    return CustomFloat


if __name__ == "__main__":
    #  todo: create tests and remove __main__
    verbose = True

    examples = (
        (Float32, "0 00000000 00000000000000000000001", 1.4E-45      ),
        (Float32, "0 10001001 00110100100111010011101", 1234.4567    ),
        (Float32, "0 01111111 00000000000000000000000", 1.0          ),
        (Float32, "0 00000000 00000000000000000000000", float("+0")  ),
        (Float32, "1 00000000 00000000000000000000000", float("-0")  ),
        (Float32, "0 11111111 00000000000000000000000", float("+inf")),
        (Float32, "1 11111111 00000000000000000000000", float("-inf")),
        (Float32, "0 11111111 10000000000000000000000", float("nan") ),
    )

    for cls, binary, original in examples:
        output = cls(binary)
        print(f"value = {output} #  (original {original})")
        if verbose:
            print(repr(output))
        print()
