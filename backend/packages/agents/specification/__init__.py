"""Specification agents for requirements processing."""

from .spec_agent import (
    APIEndpoint,
    DataModel,
    FunctionalRequirement,
    NonFunctionalRequirement,
    ServiceSpecification,
    SpecificationAgent,
)

__all__ = [
    "SpecificationAgent",
    "ServiceSpecification",
    "FunctionalRequirement",
    "NonFunctionalRequirement",
    "DataModel",
    "APIEndpoint",
]
