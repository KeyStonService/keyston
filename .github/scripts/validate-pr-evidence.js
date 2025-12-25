function validate({ context, core }) {
  const pr = context.payload.pull_request;
  const body = pr && pr.body ? pr.body : "";
  const errors = [];

  const repoRe = /(^|\n)\s*-\s*repo\s*:\s*https:\/\/github\.com\/[^\/\s]+\/[^\/\s]+(\s|$)/i;
  const branchRe = /(^|\n)\s*-\s*branch\s*:\s*\S+(\s|$)/i;
  const commitRe = /(^|\n)\s*-\s*commit(?:\s*\(40-char\s*sha\))?\s*:\s*[0-9a-f]{40}(\s|$)/i;
  const prRe = /(^|\n)\s*-\s*pr\s*:\s*https:\/\/github\.com\/[^\/\s]+\/[^\/\s]+\/pull\/\d+(\s|$)/i;

  if (!repoRe.test(body)) errors.push("缺少或格式錯誤：- repo: https://github.com/<owner>/<repo>");
  if (!branchRe.test(body)) errors.push("缺少或格式錯誤：- branch: <branch-name>");
  if (!commitRe.test(body)) errors.push("缺少或格式錯誤：- commit: <40位sha>");
  if (!prRe.test(body)) errors.push("缺少或格式錯誤：- PR: https://github.com/<owner>/<repo>/pull/<number>");

  const placeholders = [
    "<owner>", "<repo>", "<branch-name>", "<paste-full-sha-here>", "<this pr url>", "<number>", "[pr_number]", "[本 pr 編號]"
  ];
  const lowerBody = body.toLowerCase();
  const badPlaceholders = placeholders.filter((p) => lowerBody.includes(p.toLowerCase()));
  if (badPlaceholders.length > 0) {
    errors.push(`PR 仍包含未替換的 placeholder：${badPlaceholders.join(", ")}`);
  }

  if (errors.length > 0) {
    core.setFailed(
      [
        "PR 交付證據 Gate 未通過（缺一不可）。",
        "",
        "請在 PR 描述最上方加入以下四項（並填入真實值）：",
        "- repo: https://github.com/MachineNativeOps/MachineNativeOps",
        "- branch: <branch-name>",
        "- commit: <40位sha>",
        "- PR: https://github.com/MachineNativeOps/MachineNativeOps/pull/<number>",
        "",
        "錯誤清單：",
        ...errors.map((e) => `- ${e}`),
      ].join("\n")
    );
    core.setOutput("status", "FAIL");
    core.setOutput("missing-items", errors.join(","));
  } else {
    core.info("✅ PR 交付證據欄位齊全。");
    core.setOutput("status", "PASS");
    core.setOutput("missing-items", "");
  }
}

module.exports = { validatePREvidence: validate };
