from transformers import pipeline


class ModelManager:
    """
    The ModelManager class is a Singleton class designed to manage and provide access to the embedding model
    required for text processing tasks.

    This ensures that the model is loaded only once and can be reused throughout the application,
    improving efficiency and performance.

    Attributes:
        - model: Holds the pipeline for feature extraction (embedding).

    Methods:
        - initialize_model(): Initializes the embedding model.
        - get_model(): Returns the initialized embedding model.
    """

    _instance = None

    def __init__(self):
        if not self.model:
            self.initialize_model()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.initialize_model()
        return cls._instance

    def initialize_model(self):
        """Initializes the embedding model using the BGE-3 model."""
        if self.model is None:
            print("Loading the BGE-3 model...")
            self.model = pipeline("feature-extraction", model="BAAI/bge-large-en")
            print(f"Model initialized: {self.model}")
            print("Model loaded successfully.")

    def get_model(self):
        """Returns the initialized embedding model."""
        if self.model is None:
            print("Warning: Model accessed before initialization")
        return self.model
