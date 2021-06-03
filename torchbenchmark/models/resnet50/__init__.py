
# Generated by gen_torchvision_benchmark.py
import torch
import torch.optim as optim
import torchvision.models as models
from ...util.model import BenchmarkModel
from torchbenchmark.tasks import COMPUTER_VISION

#######################################################
#
#       DO NOT MODIFY THESE FILES DIRECTLY!!!
#       USE `gen_torchvision_benchmarks.py`
#
#######################################################
class Model(BenchmarkModel):
    task = COMPUTER_VISION.CLASSIFICATION
    def __init__(self, device=None, jit=False):
        super().__init__()
        self.device = device
        self.jit = jit
        self.model = models.resnet50().to(self.device)
        self.eval_model = models.resnet50().to(self.device)

        if self.jit:
            self.model = torch.jit.script(self.model)
            self.eval_model = torch.jit.script(self.eval_model)
            # model needs to in `eval`
            # in order to be optimized for inference
            self.eval_model.eval()
            self.eval_model = torch.jit.optimize_for_inference(self.eval_model)
        self.example_inputs = (torch.randn((32, 3, 224, 224)).to(self.device),)

    def get_module(self):
        return self.model, self.example_inputs

    # vision models have another model
    # instance for inference that has
    # already been optimized for inference
    def set_eval(self):
        pass

    def train(self, niter=3):
        optimizer = optim.Adam(self.model.parameters())
        loss = torch.nn.CrossEntropyLoss()
        for _ in range(niter):
            optimizer.zero_grad()
            pred = self.model(*self.example_inputs)
            y = torch.empty(pred.shape[0], dtype=torch.long, device=self.device).random_(pred.shape[1])
            loss(pred, y).backward()
            optimizer.step()

    def eval(self, niter=1):
        model = self.eval_model
        example_inputs = self.example_inputs
        example_inputs = example_inputs[0][0].unsqueeze(0)
        for i in range(niter):
            model(example_inputs)


if __name__ == "__main__":
    m = Model(device="cuda", jit=True)
    module, example_inputs = m.get_module()
    module(*example_inputs)
    m.train(niter=1)
    m.eval(niter=1)