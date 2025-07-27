"""Transform system for YAML-driven connectors."""

import logging
from typing import Any, Dict, Callable, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Transform(ABC):
    """Base class for all transforms."""
    
    @abstractmethod
    def apply(self, value: Any, context: Dict[str, Any] = None) -> Any:
        """Apply the transform to a value."""
        pass

class DateTransform(Transform):
    """Transform for parsing dates."""
    
    def apply(self, value: Any, context: Dict[str, Any] = None) -> Optional[datetime]:
        """Parse a date value using the specified format."""
        if not value:
            return None
            
        try:
            if isinstance(value, dict):
                # Handle structured date data
                year = value.get("year", "1970")
                month = value.get("month", "1")
                day = value.get("day", "1")
                
                # Handle month names
                if isinstance(month, str) and not month.isdigit():
                    month_map = {
                        "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                        "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                        "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                    }
                    month = month_map.get(month[:3], "1")
                
                return datetime(int(year), int(month), int(day))
            elif isinstance(value, str):
                # Try common date formats
                formats = [
                    "%Y-%m-%d",
                    "%Y/%m/%d",
                    "%d-%m-%Y",
                    "%d/%m/%Y",
                    "%Y%m%d"
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                        
            return None
        except (ValueError, TypeError) as e:
            logger.error(f"Error transforming date: {str(e)}")
            return None

class IntegerTransform(Transform):
    """Transform for converting values to integers."""
    
    def apply(self, value: Any, context: Dict[str, Any] = None) -> Optional[int]:
        """Convert value to integer."""
        if value is None:
            return None
            
        try:
            if isinstance(value, str):
                return int(value.strip())
            return int(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting to integer: {str(e)}")
            return None

class TextTransform(Transform):
    """Transform for text processing."""
    
    def apply(self, value: Any, context: Dict[str, Any] = None) -> Optional[str]:
        """Process text value."""
        if value is None:
            return None
            
        try:
            return str(value).strip()
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return None

class ConcatTransform(Transform):
    """Transform for concatenating multiple values."""
    
    def apply(self, value: Any, context: Dict[str, Any] = None) -> Optional[str]:
        """Concatenate values using specified separator."""
        if not isinstance(value, dict) or "fields" not in value:
            return None
            
        try:
            separator = value.get("separator", " ")
            fields = value["fields"]
            
            if not isinstance(fields, list):
                return None
                
            values = []
            for field in fields:
                if isinstance(field, dict) and "path" in field:
                    field_value = context.get("data", {}).get(field["path"])
                    if field_value:
                        values.append(str(field_value))
                elif isinstance(field, str):
                    values.append(field)
            
            return separator.join(filter(None, values))
        except Exception as e:
            logger.error(f"Error concatenating values: {str(e)}")
            return None

class TransformRegistry:
    """Registry for transform types."""
    
    _transforms: Dict[str, Transform] = {
        "date": DateTransform(),
        "integer": IntegerTransform(),
        "text": TextTransform(),
        "concat": ConcatTransform()
    }
    
    @classmethod
    def register(cls, name: str, transform: Transform) -> None:
        """Register a new transform type."""
        cls._transforms[name] = transform
        logger.info(f"Registered transform: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[Transform]:
        """Get a transform by name."""
        return cls._transforms.get(name)
    
    @classmethod
    def apply_transform(cls, transform_spec: Dict[str, Any], value: Any, context: Dict[str, Any] = None) -> Any:
        """Apply a transform based on its specification."""
        if not isinstance(transform_spec, dict) or "type" not in transform_spec:
            return value
            
        transform_type = transform_spec["type"]
        transform = cls.get(transform_type)
        
        if not transform:
            logger.warning(f"Unknown transform type: {transform_type}")
            return value
            
        try:
            return transform.apply(value, context)
        except Exception as e:
            logger.error(f"Error applying transform {transform_type}: {str(e)}")
            return value 