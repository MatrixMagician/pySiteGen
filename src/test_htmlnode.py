import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType


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


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(parent_node.to_html(), '<div class="container"><span>child</span></div>')

    def test_to_html_with_multiple_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container", "id": "main"})
        self.assertEqual(parent_node.to_html(), '<div class="container" id="main"><span>child</span></div>')

    def test_to_html_nested_parent_nodes(self):
        innermost = LeafNode("em", "emphasized")
        middle = ParentNode("strong", [innermost])
        outer = ParentNode("p", [middle])
        self.assertEqual(outer.to_html(), "<p><strong><em>emphasized</em></strong></p>")

    def test_to_html_mixed_nested_nodes(self):
        leaf1 = LeafNode("b", "Bold")
        leaf2 = LeafNode(None, " and ")
        inner_parent = ParentNode("i", [LeafNode(None, "italic")])
        parent = ParentNode("p", [leaf1, leaf2, inner_parent])
        self.assertEqual(parent.to_html(), "<p><b>Bold</b> and <i>italic</i></p>")

    def test_to_html_complex_nesting(self):
        # Test deep nesting with multiple levels
        deep_leaf = LeafNode("code", "function")
        deep_parent = ParentNode("pre", [deep_leaf])
        middle_parent = ParentNode("div", [deep_parent])
        outer_parent = ParentNode("section", [middle_parent])
        expected = "<section><div><pre><code>function</code></pre></div></section>"
        self.assertEqual(outer_parent.to_html(), expected)

    def test_to_html_no_tag_raises_error(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("tag", str(context.exception))

    def test_to_html_no_children_raises_error(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("children", str(context.exception))

    def test_to_html_empty_children_list(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_single_child(self):
        child_node = LeafNode("p", "Single child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><p>Single child</p></div>")

    def test_constructor_no_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertIsNone(parent_node.props)
        self.assertEqual(parent_node.tag, "div")
        self.assertEqual(parent_node.children, [child_node])
        self.assertIsNone(parent_node.value)

    def test_constructor_with_props(self):
        child_node = LeafNode("span", "child")
        props = {"class": "test", "id": "main"}
        parent_node = ParentNode("div", [child_node], props)
        self.assertEqual(parent_node.props, props)


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
        self.assertEqual(html_node.to_html(), "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.to_html(), "<b>Bold text</b>")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.to_html(), "<i>Italic text</i>")

    def test_code(self):
        node = TextNode("Code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "Code text")
        self.assertEqual(html_node.to_html(), "<code>Code text</code>")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})
        self.assertEqual(html_node.to_html(), '<a href="https://example.com">Click here</a>')

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.jpg", "alt": "Alt text"})
        self.assertEqual(html_node.to_html(), '<img src="https://example.com/image.jpg" alt="Alt text"></img>')

    def test_link_without_url(self):
        node = TextNode("Click here", TextType.LINK)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": None})

    def test_image_without_url(self):
        node = TextNode("Alt text", TextType.IMAGE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": None, "alt": "Alt text"})

    def test_unsupported_text_type(self):
        # Create a mock text node with an invalid text type
        node = TextNode("Test", "invalid_type")
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(node)
        self.assertIn("Unsupported text type", str(context.exception))

    def test_empty_text(self):
        node = TextNode("", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.to_html(), "")

    def test_empty_bold(self):
        node = TextNode("", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.to_html(), "<b></b>")

    def test_special_characters(self):
        node = TextNode("Text with <>&\"' characters", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.value, "Text with <>&\"' characters")

    def test_link_with_special_characters(self):
        node = TextNode("Link & text", TextType.LINK, "https://example.com?param=value&other=true")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props, {"href": "https://example.com?param=value&other=true"})


if __name__ == "__main__":
    unittest.main()