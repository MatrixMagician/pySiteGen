import unittest
from htmlnode import HTMLNode, LeafNode


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


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')
    
    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "This is raw text")
        self.assertEqual(node.to_html(), "This is raw text")
    
    def test_leaf_to_html_multiple_props(self):
        node = LeafNode("div", "Content", {"class": "container", "id": "main"})
        self.assertEqual(node.to_html(), '<div class="container" id="main">Content</div>')
    
    def test_leaf_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()
    
    def test_leaf_to_html_b_tag(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")
    
    def test_leaf_to_html_i_tag(self):
        node = LeafNode("i", "Italic text")
        self.assertEqual(node.to_html(), "<i>Italic text</i>")


if __name__ == "__main__":
    unittest.main()