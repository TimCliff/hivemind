# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class GetPostHeader(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, author=None, category=None, depth=None, permlink=None):  # noqa: E501
        """GetPostHeader - a model defined in OpenAPI

        :param author: The author of this GetPostHeader.  # noqa: E501
        :type author: str
        :param category: The category of this GetPostHeader.  # noqa: E501
        :type category: str
        :param depth: The depth of this GetPostHeader.  # noqa: E501
        :type depth: int
        :param permlink: The permlink of this GetPostHeader.  # noqa: E501
        :type permlink: str
        """
        self.openapi_types = {
            'author': str,
            'category': str,
            'depth': int,
            'permlink': str
        }

        self.attribute_map = {
            'author': 'author',
            'category': 'category',
            'depth': 'depth',
            'permlink': 'permlink'
        }

        self._author = author
        self._category = category
        self._depth = depth
        self._permlink = permlink

    @classmethod
    def from_dict(cls, dikt) -> 'GetPostHeader':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GetPostHeader of this GetPostHeader.  # noqa: E501
        :rtype: GetPostHeader
        """
        return util.deserialize_model(dikt, cls)

    @property
    def author(self):
        """Gets the author of this GetPostHeader.

        account name of the post's author  # noqa: E501

        :return: The author of this GetPostHeader.
        :rtype: str
        """
        return self._author

    @author.setter
    def author(self, author):
        """Sets the author of this GetPostHeader.

        account name of the post's author  # noqa: E501

        :param author: The author of this GetPostHeader.
        :type author: str
        """
        if author is None:
            raise ValueError("Invalid value for `author`, must not be `None`")  # noqa: E501

        self._author = author

    @property
    def category(self):
        """Gets the category of this GetPostHeader.

        post category  # noqa: E501

        :return: The category of this GetPostHeader.
        :rtype: str
        """
        return self._category

    @category.setter
    def category(self, category):
        """Sets the category of this GetPostHeader.

        post category  # noqa: E501

        :param category: The category of this GetPostHeader.
        :type category: str
        """
        if category is None:
            raise ValueError("Invalid value for `category`, must not be `None`")  # noqa: E501

        self._category = category

    @property
    def depth(self):
        """Gets the depth of this GetPostHeader.

        nesting level  # noqa: E501

        :return: The depth of this GetPostHeader.
        :rtype: int
        """
        return self._depth

    @depth.setter
    def depth(self, depth):
        """Sets the depth of this GetPostHeader.

        nesting level  # noqa: E501

        :param depth: The depth of this GetPostHeader.
        :type depth: int
        """
        if depth is None:
            raise ValueError("Invalid value for `depth`, must not be `None`")  # noqa: E501

        self._depth = depth

    @property
    def permlink(self):
        """Gets the permlink of this GetPostHeader.

        post's permlink  # noqa: E501

        :return: The permlink of this GetPostHeader.
        :rtype: str
        """
        return self._permlink

    @permlink.setter
    def permlink(self, permlink):
        """Sets the permlink of this GetPostHeader.

        post's permlink  # noqa: E501

        :param permlink: The permlink of this GetPostHeader.
        :type permlink: str
        """
        if permlink is None:
            raise ValueError("Invalid value for `permlink`, must not be `None`")  # noqa: E501

        self._permlink = permlink
