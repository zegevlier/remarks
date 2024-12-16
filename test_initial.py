import pytest
from fitz import fitz
from parsita import lit, reg, rep, Parser, opt, until, Failure
from returns.result import Success

from test_support import with_remarks
from pdf_test_support import is_valid_pdf, pdf_has_num_pages

r"""
 _____  _____  ______ 
|  __ \|  __ \|  ____|
| |__) | |  | | |__   
|  ___/| |  | |  __|  
| |    | |__| | |     
|_|    |_____/|_|     
"""
@with_remarks("demo/on-computable-numbers/xochitl")
@with_remarks("tests/in/v2_notebook_complex")
@with_remarks("tests/in/v2_book_with_ann")
def test_can_handle_drawing_with_many_scribbles():
    gosper_notebook_page_count = 3

    gosper_remarks = fitz.open("tests/out/Gosper _remarks.pdf")
    assert is_valid_pdf(gosper_remarks)
    assert gosper_remarks.page_count == gosper_notebook_page_count

    gosper_rmc = fitz.open("tests/out/Gosper _rmc.pdf")
    assert is_valid_pdf(gosper_rmc)
    assert gosper_rmc.page_count == 3


r"""
 __  __            _       _                     
|  \/  |          | |     | |                    
| \  / | __ _ _ __| | ____| | _____      ___ __  
| |\/| |/ _` | '__| |/ / _` |/ _ \ \ /\ / / '_ \ 
| |  | | (_| | |  |   < (_| | (_) \ V  V /| | | |
|_|  |_|\__,_|_|  |_|\_\__,_|\___/ \_/\_/ |_| |_|

Lessons about parsita.

1. When invoking a parser, you _must_ consume all the tokens until the EOD or you will get a failure
   You can do this with 
   `{...} << whatever`
2. When you want to extract _one_ value out of a big text. You can say the following:
   parser_that_must_exist_around_it >> parser_that_follows >> another_parser << the_parser_you_care_about >> after_the_parser_you_care_about
   So:
   `no >> yes << no` => `Success<yes>`
3. Lambdas are evil. Do not use lambdas to create abstractions.
   While it may seem attractive to write a lambda to express a common pattern, this is not a good idea.
   The operators in parsita have specific meaning, and parsita is a language expressed with operators.
   When you write a function, the result of the operator is lost.
"""


def assert_parser_succeeds(parser: Parser, input_string: str, expected_output=None):
    result = parser.parse(input_string)
    match result:
        case Success(value):
            output = value
            if expected_output:
                assert expected_output == output
        case Failure(error):
            raise error
    assert type(result) is Success, result.failure()


any_char = reg(r'.') | lit("\n")
whatever = rep(any_char)
newline = lit('\n')

to_newline = reg(r'[^\n]+')

obsidian_tag = reg(r"#([a-z/])+")
frontmatter = opt(
    lit('---') >> newline >>
    lit("tags") >> lit(":\n") >> lit("- ") >> lit("'") >> obsidian_tag << lit("'") << rep(newline) <<
    lit("---") << rep(newline)
)
autogeneration_warning = lit("""> [!WARNING] **Do not modify** this file
> This file is automatically generated by Scrybble and will be overwritten whenever this file in synchronized.
> Treat it as a reference.""")
h = lambda n, c: lit(n + " ") >> c

@with_remarks("tests/in/highlighter-test")
@pytest.mark.markdown
def test_generated_markdown_has_autogeneration_warning():
    has_warning = (until(autogeneration_warning) << autogeneration_warning >> whatever)
    with open("tests/out/docsfordevelopers _obsidian.md") as f:
        assert_parser_succeeds(has_warning, f.read())

@with_remarks("tests/in/v3_markdown_tags")
@pytest.mark.markdown
def test_yaml_frontmatter_is_valid():
    with open('tests/out/tags test _obsidian.md') as f:
        content = f.read()
        assert_parser_succeeds(frontmatter << whatever, content, ["#remarkable/obsidian"])


# @with_remarks("tests/in/v3_markdown_tags")
# @with_remarks("tests/in/highlighter-test")
# @pytest.mark.markdown
# def test_generated_markdown_heading_is_positioned_correctly():
#     rmdoc_title = h("#", to_newline)
#
#     with open("tests/out/docsfordevelopers _obsidian.md") as f:
#         content = f.read()
#         assert_parser_succeeds(frontmatter >> rmdoc_title << whatever, content, "docsfordevelopers")
#     with open("tests/out/tags test _obsidian.md") as f:
#         content = f.read()
#         assert_parser_succeeds(frontmatter >> rmdoc_title << whatever, content, "tags test")



# @with_remarks("tests/in/v3_typed_text")
# def test_something():
#     raise Exception("hi")
