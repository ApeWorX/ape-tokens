from ape_tokens import tokens


def test_tokens():
    assert tokens is not None

    # Show is the same
    from ape_tokens import tokens as tokens2

    assert id(tokens2) == id(tokens)
