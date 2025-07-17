import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("This is a link", TextType.LINK, "https://example.com")
        node2 = TextNode("This is a link", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)
    
    def test_eq_with_none_url(self):
        node = TextNode("This is text", TextType.TEXT, None)
        node2 = TextNode("This is text", TextType.TEXT, None)
        self.assertEqual(node, node2)
    
    def test_not_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is different text", TextType.BOLD)
        self.assertNotEqual(node, node2)
    
    def test_not_eq_different_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
    
    def test_not_eq_different_url(self):
        node = TextNode("This is a link", TextType.LINK, "https://example.com")
        node2 = TextNode("This is a link", TextType.LINK, "https://different.com")
        self.assertNotEqual(node, node2)
    
    def test_not_eq_url_vs_none(self):
        node = TextNode("This is text", TextType.TEXT, "https://example.com")
        node2 = TextNode("This is text", TextType.TEXT, None)
        self.assertNotEqual(node, node2)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_bold_delimiter(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_italic_delimiter(self):
        node = TextNode("This is text with an *italic* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple_delimiters(self):
        node = TextNode("This has `code` and **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and **bold** text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple_same_delimiters(self):
        node = TextNode("This has `first` and `second` code blocks", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("first", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.CODE),
            TextNode(" code blocks", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_no_delimiter(self):
        node = TextNode("This is just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [node]
        self.assertEqual(new_nodes, expected)

    def test_split_non_text_node(self):
        node = TextNode("bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [node]
        self.assertEqual(new_nodes, expected)

    def test_split_mixed_node_types(self):
        nodes = [
            TextNode("This is text with `code`", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with `inline code`", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("inline code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_empty_delimiter_content(self):
        node = TextNode("This has `` empty code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode(" empty code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_delimiter_at_start(self):
        node = TextNode("`code` at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_delimiter_at_end(self):
        node = TextNode("Text ends with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text ends with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_only_delimiter(self):
        node = TextNode("`code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_unclosed_delimiter_raises_error(self):
        node = TextNode("This has `unclosed delimiter", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("unclosed delimiter", str(context.exception))

    def test_split_multiple_unclosed_delimiters(self):
        node = TextNode("This has `one and `two and `three unclosed", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_split_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = []
        self.assertEqual(new_nodes, expected)

    def test_split_whitespace_only_delimiter(self):
        node = TextNode("Text with ` ` space code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode(" ", TextType.CODE),
            TextNode(" space code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_consecutive_delimiters(self):
        node = TextNode("Text with `first``second` consecutive", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("first", TextType.CODE),
            TextNode("second", TextType.CODE),
            TextNode(" consecutive", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_no_images(self):
        text = "This is text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_empty_alt_text(self):
        text = "This has an image with empty alt text ![](https://example.com/image.png)"
        matches = extract_markdown_images(text)
        expected = [("", "https://example.com/image.png")]
        self.assertListEqual(expected, matches)

    def test_extract_complex_alt_text(self):
        text = "Image with spaces ![my awesome image](https://example.com/image.png)"
        matches = extract_markdown_images(text)
        expected = [("my awesome image", "https://example.com/image.png")]
        self.assertListEqual(expected, matches)

    def test_extract_image_with_special_chars_in_url(self):
        text = "Image with special chars ![test](https://example.com/path/to/image.png?param=value&other=123)"
        matches = extract_markdown_images(text)
        expected = [("test", "https://example.com/path/to/image.png?param=value&other=123")]
        self.assertListEqual(expected, matches)

    def test_extract_image_mixed_with_links(self):
        text = "Text with ![image](https://i.imgur.com/image.png) and [link](https://example.com)"
        matches = extract_markdown_images(text)
        expected = [("image", "https://i.imgur.com/image.png")]
        self.assertListEqual(expected, matches)

    def test_extract_image_at_start_and_end(self):
        text = "![start](https://example.com/start.png) middle text ![end](https://example.com/end.png)"
        matches = extract_markdown_images(text)
        expected = [("start", "https://example.com/start.png"), ("end", "https://example.com/end.png")]
        self.assertListEqual(expected, matches)

    def test_extract_image_with_numbers_in_alt(self):
        text = "Image with numbers ![image123](https://example.com/123.png)"
        matches = extract_markdown_images(text)
        expected = [("image123", "https://example.com/123.png")]
        self.assertListEqual(expected, matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_single_link(self):
        text = "Check out this [awesome site](https://example.com)"
        matches = extract_markdown_links(text)
        expected = [("awesome site", "https://example.com")]
        self.assertListEqual(expected, matches)

    def test_extract_no_links(self):
        text = "This is text with no links"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_extract_empty_anchor_text(self):
        text = "This has a link with empty anchor text [](https://example.com)"
        matches = extract_markdown_links(text)
        expected = [("", "https://example.com")]
        self.assertListEqual(expected, matches)

    def test_extract_link_with_special_chars(self):
        text = "Link with special chars [test-link_123](https://example.com/path?param=value&other=123)"
        matches = extract_markdown_links(text)
        expected = [("test-link_123", "https://example.com/path?param=value&other=123")]
        self.assertListEqual(expected, matches)

    def test_extract_link_mixed_with_images(self):
        text = "Text with [link](https://example.com) and ![image](https://i.imgur.com/image.png)"
        matches = extract_markdown_links(text)
        expected = [("link", "https://example.com")]
        self.assertListEqual(expected, matches)

    def test_extract_multiple_links_same_line(self):
        text = "Multiple [first](https://one.com) and [second](https://two.com) and [third](https://three.com) links"
        matches = extract_markdown_links(text)
        expected = [("first", "https://one.com"), ("second", "https://two.com"), ("third", "https://three.com")]
        self.assertListEqual(expected, matches)

    def test_extract_link_at_start_and_end(self):
        text = "[start](https://start.com) middle text [end](https://end.com)"
        matches = extract_markdown_links(text)
        expected = [("start", "https://start.com"), ("end", "https://end.com")]
        self.assertListEqual(expected, matches)

    def test_extract_link_with_spaces_in_anchor(self):
        text = "Link with spaces [my awesome link](https://example.com)"
        matches = extract_markdown_links(text)
        expected = [("my awesome link", "https://example.com")]
        self.assertListEqual(expected, matches)

    def test_extract_link_ignores_images(self):
        text = "Should not match images ![not a link](https://example.com) but should match [actual link](https://example.com)"
        matches = extract_markdown_links(text)
        expected = [("actual link", "https://example.com")]
        self.assertListEqual(expected, matches)

    def test_extract_adjacent_image_and_link(self):
        text = "Adjacent ![image](https://img.com)[link](https://link.com) elements"
        matches = extract_markdown_links(text)
        expected = [("link", "https://link.com")]
        self.assertListEqual(expected, matches)

    def test_extract_nested_brackets_in_anchor(self):
        text = "Text with [anchor [nested]](https://example.com) test"
        matches = extract_markdown_links(text)
        # This should not match due to nested brackets
        expected = []
        self.assertListEqual(expected, matches)

if __name__ == "__main__":
    unittest.main()
