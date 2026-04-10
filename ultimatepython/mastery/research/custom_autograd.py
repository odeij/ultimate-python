"""
Custom Autograd — implementing automatic differentiation from scratch.

This module builds a minimal autograd engine to show you what PyTorch's
autograd is ACTUALLY doing. Understanding this will make you a better
AI researcher because you will:
  - Know why .backward() works the way it does
  - Be able to write custom backward passes for novel operations
  - Debug gradient flow issues from first principles
  - Read PyTorch source code with confidence

Connection to PyTorch:
  - Tensor         ->  Value (our minimal version)
  - .grad          ->  .grad
  - .backward()    ->  .backward()
  - torch.no_grad  ->  similar to not calling backward

Concepts covered:
  1. Forward pass: compute values, record the computation graph
  2. Backward pass: topological sort + chain rule accumulation
  3. Implementing +, *, **, tanh as differentiable operations
  4. Using the engine to train a simple neuron
"""

import math
from typing import Optional, Callable


class Value:
    """A scalar value with automatic differentiation support.

    This is a minimal version of PyTorch's Tensor (scalar case).
    Each Value stores:
      - data: the actual scalar value
      - grad: the gradient accumulated during backward pass
      - _backward: the local gradient function for this operation
      - _prev: the set of input Values that produced this Value
    """

    def __init__(self, data: float,
                 _children: tuple["Value", ...] = (),
                 _op: str = ""):
        self.data = float(data)
        self.grad = 0.0           # dL/d(self), accumulates during backward
        self._backward: Callable[[], None] = lambda: None
        self._prev = set(_children)
        self._op = _op            # for debugging: which op created this node

    def __repr__(self) -> str:
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

    # -----------------------------------------------------------------------
    # Forward operations — each defines its own local gradient rule
    # -----------------------------------------------------------------------

    def __add__(self, other: "Value | float") -> "Value":
        """Addition: d/dx(x + y) = 1 for both x and y."""
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward() -> None:
            # Gradient flows unchanged through addition
            self.grad += out.grad   # += because multiple paths can contribute
            other.grad += out.grad

        out._backward = _backward
        return out

    def __radd__(self, other: "Value | float") -> "Value":
        return self + other

    def __mul__(self, other: "Value | float") -> "Value":
        """Multiplication: d/dx(x*y) = y, d/dy(x*y) = x."""
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward() -> None:
            self.grad += other.data * out.grad    # chain rule: dL/dx = y * dL/dout
            other.grad += self.data * out.grad    # chain rule: dL/dy = x * dL/dout

        out._backward = _backward
        return out

    def __rmul__(self, other: "Value | float") -> "Value":
        return self * other

    def __pow__(self, exponent: float) -> "Value":
        """Power: d/dx(x^n) = n * x^(n-1)."""
        out = Value(self.data ** exponent, (self,), f"**{exponent}")

        def _backward() -> None:
            self.grad += exponent * (self.data ** (exponent - 1)) * out.grad

        out._backward = _backward
        return out

    def __neg__(self) -> "Value":
        return self * -1

    def __sub__(self, other: "Value | float") -> "Value":
        return self + (-other if isinstance(other, Value) else Value(-other))

    def __rsub__(self, other: "Value | float") -> "Value":
        return Value(other) - self

    def __truediv__(self, other: "Value | float") -> "Value":
        return self * (other ** -1 if isinstance(other, Value) else Value(other) ** -1)

    def tanh(self) -> "Value":
        """Hyperbolic tangent: d/dx(tanh(x)) = 1 - tanh(x)^2."""
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward() -> None:
            self.grad += (1 - t ** 2) * out.grad

        out._backward = _backward
        return out

    def relu(self) -> "Value":
        """ReLU: d/dx(relu(x)) = 1 if x > 0 else 0."""
        out = Value(max(0, self.data), (self,), "relu")

        def _backward() -> None:
            self.grad += (out.data > 0) * out.grad

        out._backward = _backward
        return out

    def exp(self) -> "Value":
        """Exponential: d/dx(exp(x)) = exp(x)."""
        e = math.exp(self.data)
        out = Value(e, (self,), "exp")

        def _backward() -> None:
            self.grad += e * out.grad

        out._backward = _backward
        return out

    # -----------------------------------------------------------------------
    # Backward pass — topological sort + accumulate gradients
    # -----------------------------------------------------------------------

    def backward(self) -> None:
        """Compute gradients via reverse-mode autodiff (backpropagation).

        Steps:
          1. Build topological order of the computation graph
          2. Set gradient of this (loss) node to 1.0 (dL/dL = 1)
          3. Walk backward in topological order, calling each node's _backward
        """
        topo: list[Value] = []
        visited: set[int] = set()

        def build_topo(v: Value) -> None:
            if id(v) not in visited:
                visited.add(id(v))
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        self.grad = 1.0   # seed: dL/dL = 1
        for node in reversed(topo):
            node._backward()


# ---------------------------------------------------------------------------
# Neuron — a single artificial neuron using our autograd engine
# ---------------------------------------------------------------------------

class Neuron:
    """A single neuron: output = activation(w . x + b)."""

    def __init__(self, n_inputs: int):
        import random
        self.weights = [Value(random.uniform(-1, 1)) for _ in range(n_inputs)]
        self.bias = Value(0.0)

    def __call__(self, x: list[float | Value]) -> Value:
        inputs = [xi if isinstance(xi, Value) else Value(xi) for xi in x]
        activation = sum(w * xi for w, xi in zip(self.weights, inputs)) + self.bias
        return activation.tanh()

    def parameters(self) -> list[Value]:
        return self.weights + [self.bias]


# ---------------------------------------------------------------------------
# Training loop demonstration
# ---------------------------------------------------------------------------

def train_neuron() -> None:
    """Train a single neuron to learn the AND gate.

    This is the same training loop as PyTorch, just scalar:
      1. Forward pass: compute output
      2. Compute loss (MSE)
      3. Zero gradients
      4. Backward pass: compute gradients
      5. Update parameters (gradient descent step)
    """
    neuron = Neuron(2)
    # AND gate truth table
    X = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    Y = [-1.0, -1.0, -1.0, 1.0]  # tanh output: -1 = False, 1 = True

    learning_rate = 0.1
    for step in range(100):
        # Forward pass
        outputs = [neuron(x) for x in X]

        # MSE loss
        loss = sum((out - y) ** 2 for out, y in zip(outputs, Y)) * (1 / len(Y))

        # Zero gradients (equivalent to optimizer.zero_grad() in PyTorch)
        for p in neuron.parameters():
            p.grad = 0.0

        # Backward pass
        loss.backward()

        # SGD update
        for p in neuron.parameters():
            p.data -= learning_rate * p.grad

    # After training, check that predictions have the right sign
    preds = [neuron(x).data for x in X]
    assert preds[3] > 0    # [1,1] -> AND = True
    assert preds[0] < 0    # [0,0] -> AND = False
    assert preds[1] < 0    # [0,1] -> AND = False
    assert preds[2] < 0    # [1,0] -> AND = False


def main() -> None:
    # Test basic operations and gradients
    x = Value(2.0)
    y = Value(3.0)

    # z = x^2 + y  =>  dz/dx = 2x = 4,  dz/dy = 1
    z = x ** 2 + y
    z.backward()
    assert abs(x.grad - 4.0) < 1e-6
    assert abs(y.grad - 1.0) < 1e-6

    # Test tanh gradient: d/dx(tanh(x)) at x=0 = 1
    a = Value(0.0)
    b = a.tanh()
    b.backward()
    assert abs(a.grad - 1.0) < 1e-6

    # Test chain rule: d/dx(tanh(x^2)) at x=1
    # = tanh'(1) * 2x = (1 - tanh(1)^2) * 2
    c = Value(1.0)
    d = (c ** 2).tanh()
    d.backward()
    expected = (1 - math.tanh(1.0) ** 2) * 2.0
    assert abs(c.grad - expected) < 1e-6

    # Train the neuron
    train_neuron()


if __name__ == "__main__":
    main()
