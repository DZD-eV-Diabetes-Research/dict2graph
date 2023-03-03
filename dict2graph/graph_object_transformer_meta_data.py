from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from dict2graph.transformers._base import _NodeTransformerBase


class NoDefault:
    pass


class TransformerMetaDataMixin:
    def __init__(self):
        self._transformer_meta_data = {}

    def set_transformer_meta_data(
        self, transformer: "_NodeTransformerBase", key: str, val: Any
    ):
        """Support function to give the transformers the possibility to safe a state into a node or relationship

        Args:
            transformer (_NodeTransformerBase): _description_
            key (str): _description_
            val (Any): _description_
        """
        if not transformer in self._transformer_meta_data:
            self._transformer_meta_data[transformer] = {}
        self._transformer_meta_data[transformer][key] = val

    def get_transformer_meta_data(
        self, transformer: "_NodeTransformerBase", key: str, default: Any = NoDefault
    ):
        """Support function to give the transformers the possibility to get a saved state from a node or relationship

        Args:
            transformer (_NodeTransformerBase): _description_
            key (str): _description_
            default (Any, optional): _description_. Defaults to NoDefault.

        Raises:
            f: _description_
            f: _description_

        Returns:
            _type_: _description_
        """
        if not transformer in self._transformer_meta_data:
            if default != NoDefault:
                return default
            else:
                raise f"No Transformer meta data found in Node {self} for Transformer {transformer.__class__}."
        if not key in self._transformer_meta_data[transformer]:
            if default != NoDefault:
                return default
            else:
                raise f"No transformer meta data key '{key}' found in Node {self} for Transformer {transformer.__class__}."
        return self._transformer_meta_data[transformer][key]
