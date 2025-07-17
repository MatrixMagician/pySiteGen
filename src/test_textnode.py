import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, BlockType, block_to_block_type, text_to_children, markdown_to_html_node, extract_title


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


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode("Text with ![single image](https://example.com/image.png) here", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("single image", TextType.IMAGE, "https://example.com/image.png"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_start(self):
        node = TextNode("![start image](https://example.com/start.png) text after", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start image", TextType.IMAGE, "https://example.com/start.png"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_end(self):
        node = TextNode("Text before ![end image](https://example.com/end.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("end image", TextType.IMAGE, "https://example.com/end.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_only(self):
        node = TextNode("![only image](https://example.com/only.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("only image", TextType.IMAGE, "https://example.com/only.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [node]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        expected = [node]
        self.assertListEqual(expected, new_nodes)

    def test_split_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = []
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_nodes_mixed(self):
        nodes = [
            TextNode("Text with ![image1](https://example.com/1.png) here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with ![image2](https://example.com/2.png) there", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("image1", TextType.IMAGE, "https://example.com/1.png"),
            TextNode(" here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("image2", TextType.IMAGE, "https://example.com/2.png"),
            TextNode(" there", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_empty_alt_text(self):
        node = TextNode("Text with ![](https://example.com/empty.png) image", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("", TextType.IMAGE, "https://example.com/empty.png"),
            TextNode(" image", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_consecutive_images(self):
        node = TextNode("![first](https://example.com/1.png)![second](https://example.com/2.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("first", TextType.IMAGE, "https://example.com/1.png"),
            TextNode("second", TextType.IMAGE, "https://example.com/2.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_with_links(self):
        node = TextNode("Text with ![image](https://example.com/img.png) and [link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" and [link](https://example.com)", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_single_link(self):
        node = TextNode("Text with [single link](https://example.com) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("single link", TextType.LINK, "https://example.com"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_start(self):
        node = TextNode("[start link](https://example.com/start) text after", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start link", TextType.LINK, "https://example.com/start"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_end(self):
        node = TextNode("Text before [end link](https://example.com/end)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("end link", TextType.LINK, "https://example.com/end"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_only(self):
        node = TextNode("[only link](https://example.com/only)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("only link", TextType.LINK, "https://example.com/only"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [node]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        expected = [node]
        self.assertListEqual(expected, new_nodes)

    def test_split_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = []
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_nodes_mixed(self):
        nodes = [
            TextNode("Text with [link1](https://example.com/1) here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with [link2](https://example.com/2) there", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("link1", TextType.LINK, "https://example.com/1"),
            TextNode(" here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("More text with ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "https://example.com/2"),
            TextNode(" there", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_empty_anchor_text(self):
        node = TextNode("Text with [](https://example.com/empty) link", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("", TextType.LINK, "https://example.com/empty"),
            TextNode(" link", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_consecutive_links(self):
        node = TextNode("[first](https://example.com/1)[second](https://example.com/2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("first", TextType.LINK, "https://example.com/1"),
            TextNode("second", TextType.LINK, "https://example.com/2"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_with_images(self):
        node = TextNode("Text with [link](https://example.com) and ![image](https://example.com/img.png)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" and ![image](https://example.com/img.png)", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_ignores_images(self):
        node = TextNode("Text with ![not link](https://example.com) and [actual link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text with ![not link](https://example.com) and ", TextType.TEXT),
            TextNode("actual link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_with_special_chars(self):
        node = TextNode("Link with [special-chars_123](https://example.com/path?param=value&other=123) text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with ", TextType.TEXT),
            TextNode("special-chars_123", TextType.LINK, "https://example.com/path?param=value&other=123"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_mixed_images_and_links(self):
        node = TextNode("Text ![img](https://img.com) and [link](https://link.com) mixed", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text ![img](https://img.com) and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
            TextNode(" mixed", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_full_example(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text with no formatting"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text with no formatting", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_bold(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_italic(self):
        text = "This is *italic* text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_code(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_image(self):
        text = "This is ![image](https://example.com/image.png) text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_link(self):
        text = "This is [link](https://example.com) text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_same_type(self):
        text = "This is **bold** and **more bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("more bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_nested_formatting(self):
        text = "This is **bold with `code` inside** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold with `code` inside", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_separate_formatting(self):
        text = "This is **bold** and `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_mixed_images_and_links(self):
        text = "Check out ![image](https://example.com/img.png) and [link](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Check out ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_consecutive_formatting(self):
        text = "**bold***italic*`code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_all_at_start(self):
        text = "**bold** *italic* `code` ![image](https://example.com/img.png) [link](https://example.com) end"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_complex_mixed(self):
        text = "Start **bold** then *italic* with `code` and ![img](https://img.com) plus [link](https://link.com) end"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" then ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "https://img.com"),
            TextNode(" plus ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_empty_text(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = []
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_whitespace_only(self):
        text = "   "
        nodes = text_to_textnodes(text)
        expected = [TextNode("   ", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_single_character_formatting(self):
        text = "A **b** c"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("A ", TextType.TEXT),
            TextNode("b", TextType.BOLD),
            TextNode(" c", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "This is just a single paragraph with no double newlines"
        blocks = markdown_to_blocks(md)
        expected = ["This is just a single paragraph with no double newlines"]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        expected = []
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        expected = []
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_with_headings(self):
        md = """# This is a heading

This is a paragraph of text.

## This is a subheading

Another paragraph here."""
        blocks = markdown_to_blocks(md)
        expected = [
            "# This is a heading",
            "This is a paragraph of text.",
            "## This is a subheading",
            "Another paragraph here.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_with_code_blocks(self):
        md = """This is a paragraph.

```python
def hello():
    print("Hello, world!")
```

Another paragraph."""
        blocks = markdown_to_blocks(md)
        expected = [
            "This is a paragraph.",
            "```python\ndef hello():\n    print(\"Hello, world!\")\n```",
            "Another paragraph.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_with_quotes(self):
        md = """This is a paragraph.

> This is a quote
> that spans multiple lines

Another paragraph."""
        blocks = markdown_to_blocks(md)
        expected = [
            "This is a paragraph.",
            "> This is a quote\n> that spans multiple lines",
            "Another paragraph.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_multiple_newlines(self):
        md = """First paragraph.



Second paragraph.




Third paragraph."""
        blocks = markdown_to_blocks(md)
        expected = [
            "First paragraph.",
            "Second paragraph.",
            "Third paragraph.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_leading_trailing_whitespace(self):
        md = """   
   
First paragraph with leading whitespace.

   Second paragraph with trailing whitespace.   

   Third paragraph with both.   
   
   """
        blocks = markdown_to_blocks(md)
        expected = [
            "First paragraph with leading whitespace.",
            "Second paragraph with trailing whitespace.",
            "Third paragraph with both.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_mixed_content(self):
        md = """# Main Title

This is an introduction paragraph.

## Features

- Feature one
- Feature two
- Feature three

### Code Example

```python
print("Hello!")
```

> Important note: This is a quote block.

Final paragraph."""
        blocks = markdown_to_blocks(md)
        expected = [
            "# Main Title",
            "This is an introduction paragraph.",
            "## Features",
            "- Feature one\n- Feature two\n- Feature three",
            "### Code Example",
            "```python\nprint(\"Hello!\")\n```",
            "> Important note: This is a quote block.",
            "Final paragraph.",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_single_newlines_preserved(self):
        md = """Line one
Line two
Line three

New paragraph
With multiple lines
Here too"""
        blocks = markdown_to_blocks(md)
        expected = [
            "Line one\nLine two\nLine three",
            "New paragraph\nWith multiple lines\nHere too",
        ]
        self.assertEqual(expected, blocks)

    def test_markdown_to_blocks_no_double_newlines(self):
        md = "Single line with no double newlines"
        blocks = markdown_to_blocks(md)
        expected = ["Single line with no double newlines"]
        self.assertEqual(expected, blocks)


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type_heading_h1(self):
        block = "# This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading_h2(self):
        block = "## This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading_h6(self):
        block = "###### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_heading_invalid_too_many_hashes(self):
        block = "####### This is not a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_heading_no_space(self):
        block = "#This is not a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_code_block(self):
        block = "```python\nprint('Hello')\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_code_block_empty(self):
        block = "```\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_code_block_single_line(self):
        block = "```code```"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_code_block_no_end(self):
        block = "```python\nprint('Hello')"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_quote_single_line(self):
        block = "> This is a quote"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.QUOTE, block_type)

    def test_block_to_block_type_quote_multiple_lines(self):
        block = "> This is a quote\n> that spans multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.QUOTE, block_type)

    def test_block_to_block_type_quote_mixed_lines(self):
        block = "> This is a quote\nThis is not"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_unordered_list_single_item(self):
        block = "- This is a list item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.UNORDERED_LIST, block_type)

    def test_block_to_block_type_unordered_list_multiple_items(self):
        block = "- First item\n- Second item\n- Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.UNORDERED_LIST, block_type)

    def test_block_to_block_type_unordered_list_no_space(self):
        block = "-This is not a list item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_unordered_list_mixed_lines(self):
        block = "- This is a list item\nThis is not"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_ordered_list_single_item(self):
        block = "1. This is a list item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.ORDERED_LIST, block_type)

    def test_block_to_block_type_ordered_list_multiple_items(self):
        block = "1. First item\n2. Second item\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.ORDERED_LIST, block_type)

    def test_block_to_block_type_ordered_list_wrong_numbering(self):
        block = "1. First item\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_ordered_list_not_starting_with_1(self):
        block = "2. Second item\n3. Third item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_ordered_list_no_space(self):
        block = "1.This is not a list item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_ordered_list_mixed_lines(self):
        block = "1. This is a list item\nThis is not"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_plain_text(self):
        block = "This is just a regular paragraph"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_multiple_lines(self):
        block = "This is a paragraph\nthat spans multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_with_formatting(self):
        block = "This is a paragraph with **bold** and *italic* text"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_hash_in_middle(self):
        block = "This # is not a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_backticks_in_middle(self):
        block = "This has ```code``` in the middle"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_quote_in_middle(self):
        block = "This has > quote in the middle"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_paragraph_dash_in_middle(self):
        block = "This has - dash in the middle"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_empty_lines_in_ordered_list(self):
        block = "1. First item\n\n2. Second item"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.PARAGRAPH, block_type)

    def test_block_to_block_type_quote_with_space_after(self):
        block = "> This is a quote\n> with proper spacing"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.QUOTE, block_type)

    def test_block_to_block_type_code_block_with_language(self):
        block = "```python\ndef hello():\n    print('Hello')\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.CODE, block_type)

    def test_block_to_block_type_heading_with_multiple_words(self):
        block = "### This is a longer heading with multiple words"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.HEADING, block_type)

    def test_block_to_block_type_ordered_list_double_digits(self):
        block = "1. First\n2. Second\n3. Third\n4. Fourth\n5. Fifth\n6. Sixth\n7. Seventh\n8. Eighth\n9. Ninth\n10. Tenth"
        block_type = block_to_block_type(block)
        self.assertEqual(BlockType.ORDERED_LIST, block_type)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = """
# This is a heading

## This is a subheading
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is a heading</h1><h2>This is a subheading</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

This is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a\nblockquote block</blockquote><p>This is paragraph text</p></div>",
        )

    def test_unordered_list(self):
        md = """
- This is a list
- with items
- and *more* items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. This is an ordered list
2. with items
3. and *more* items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>This is an ordered list</li><li>with items</li><li>and <i>more</i> items</li></ol></div>",
        )

    def test_multiple_block_types(self):
        md = """
# Main heading

This is a paragraph with **bold** text.

## Subheading

> This is a quote

- First item
- Second item

1. Ordered first
2. Ordered second

```
def hello():
    print("Hello!")
```

Final paragraph.
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = (
            "<div>"
            "<h1>Main heading</h1>"
            "<p>This is a paragraph with <b>bold</b> text.</p>"
            "<h2>Subheading</h2>"
            "<blockquote>This is a quote</blockquote>"
            "<ul><li>First item</li><li>Second item</li></ul>"
            "<ol><li>Ordered first</li><li>Ordered second</li></ol>"
            "<pre><code>def hello():\n    print(\"Hello!\")\n</code></pre>"
            "<p>Final paragraph.</p>"
            "</div>"
        )
        self.assertEqual(html, expected)

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_single_paragraph(self):
        md = "Just a single paragraph"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Just a single paragraph</p></div>")

    def test_heading_with_formatting(self):
        md = "# This is a heading with **bold** text"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>This is a heading with <b>bold</b> text</h1></div>")

    def test_code_block_with_language(self):
        md = """
```python
def hello():
    print("Hello!")
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>python\ndef hello():\n    print(\"Hello!\")\n</code></pre></div>",
        )

class TestExtractTitle(unittest.TestCase):
    def test_extract_title_basic(self):
        markdown = "# Hello"
        title = extract_title(markdown)
        self.assertEqual(title, "Hello")

    def test_extract_title_with_extra_whitespace(self):
        markdown = "#   Hello World   "
        title = extract_title(markdown)
        self.assertEqual(title, "Hello World")

    def test_extract_title_with_other_content(self):
        markdown = """Some text before

# Main Title

Some text after"""
        title = extract_title(markdown)
        self.assertEqual(title, "Main Title")

    def test_extract_title_with_formatting(self):
        markdown = "# This is a **bold** title"
        title = extract_title(markdown)
        self.assertEqual(title, "This is a **bold** title")

    def test_extract_title_multiline(self):
        markdown = """This is a paragraph

# The Real Title

## Not this one

Another paragraph"""
        title = extract_title(markdown)
        self.assertEqual(title, "The Real Title")

    def test_extract_title_leading_whitespace(self):
        markdown = "   # Indented Title   "
        title = extract_title(markdown)
        self.assertEqual(title, "Indented Title")

    def test_extract_title_no_h1_header(self):
        markdown = """## This is h2

### This is h3

Regular paragraph text"""
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")

    def test_extract_title_empty_markdown(self):
        markdown = ""
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")

    def test_extract_title_hash_without_space(self):
        markdown = "#NotATitle"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")

    def test_extract_title_multiple_h1_headers(self):
        markdown = """# First Title

Some content

# Second Title"""
        title = extract_title(markdown)
        self.assertEqual(title, "First Title")

    def test_extract_title_empty_h1(self):
        markdown = "#  "
        title = extract_title(markdown)
        self.assertEqual(title, "")

    def test_extract_title_with_special_characters(self):
        markdown = "# Title with $pecial Ch@racters & Symbols!"
        title = extract_title(markdown)
        self.assertEqual(title, "Title with $pecial Ch@racters & Symbols!")


if __name__ == "__main__":
    unittest.main()
