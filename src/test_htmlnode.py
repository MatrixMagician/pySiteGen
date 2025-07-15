import unittest
from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_props(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        node = HTMLNode(props=props)
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_without_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        props = {"class": "button"}
        node = HTMLNode(props=props)
        expected = ' class="button"'
        self.assertEqual(node.props_to_html(), expected)

    def test_repr(self):
        node = HTMLNode(tag="p", value="Hello world", children=None, props={"class": "text"})
        expected = "HTMLNode(tag=p, value=Hello world, children=None, props={'class': 'text'})"
        self.assertEqual(repr(node), expected)

    def test_to_html_raises_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()