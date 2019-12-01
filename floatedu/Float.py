
__all__ = (
    "Float8", "Float16", "BFloat16", "Float32", "Float64", "Float128",
)


# noinspection PyMethodParameters
class Float(list):
    def __init__(f, binary_str):
        if type(f) == Float:
            # It's supposed to be subclassed and have k, p, and
            # bias values set.
            raise RuntimeError("Not supposed to be used directly")

        super().__init__(f)

        # Strip spaces and underscores
        bits = binary_str.replace(" ", "").replace("_", "")

        # Partition bits according to k and p value
        parts = _int_partitions(bits, 1, f.k, f.p - 1)
        f.extend(parts)

    @property
    def sign_bit(f): return f[0]
    
    @property
    def exponent_bits(f): return f[1]
    
    @property
    def fraction_bits(f): return f[2]

    @property
    def kind(f):
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
        return (-1)**f.sign_bit[0]

    @property
    def exponent(f):
        #  exponent = int("".join(map(str, f.exponent_bits)), 2)
        exponent = 0
        for bit, n in zip(f.exponent_bits, range(f.k)[::-1]):  # k..0
            if bit:
                exponent += 2**n
        return exponent

    @property
    def fraction(f):
        fraction = 0
        for bit, n in zip(f.fraction_bits, range(1, f.p)):  # 1..(p-1)
            if bit:
                fraction += 2**-n
        return fraction

    @property
    def significand(f):
        if f.kind == "subnormal":
            return 0 + f.fraction
        if f.kind == "normal":
            return 1 + f.fraction
        else:
            return None

    @property
    def str_bits(f):
        return "{}_{}_{}".format(
            f.sign_bit[0],
            "".join(map(str, f.exponent_bits)),
            "".join(map(str, f.fraction_bits)),
        )

    @property
    def as_dict(f):
        return {
            k: getattr(f, k)
            for k in (
                "value", "kind", "k", "p", "bias", "str_bits", "sign",
                "exponent", "fraction", "significand"
            )
        }

    def __repr__(f):
        return (
            f"{{'value': {f.value},\n"
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


class Float16(Float):  (k, p, bias) = 5,  11,  15
class BFloat16(Float): (k, p, bias) = 8,  8,   127
class Float32(Float):  (k, p, bias) = 8,  24,  127
class Float64(Float):  (k, p, bias) = 11, 53,  1023
class Float128(Float): (k, p, bias) = 15, 113, 16383
class Float256(Float): (k, p, bias) = 19, 237, 262143


def _int_partitions(s, *lengths):
    end = 0
    for length in lengths:
        start, end = end, end + length
        yield list(map(int, s[start:end]))

def new_float_class(name, n_exponent, n_significand, exponent_bias):
    """
    Create new class subclassing FloatImplementation and setting up
    p, k, and bias values.

    :param n_exponent number of bits of the exponent
    :param n_significand number of bits (implicit one included) of the
        significand
    :param exponent_bias exponent bias
    """
    class CustomFloat(Float):
        k, p, bias, = n_exponent, n_significand, exponent_bias
        __qualname__ = __name__ = name
    return CustomFloat


if __name__ == "__main__":
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
