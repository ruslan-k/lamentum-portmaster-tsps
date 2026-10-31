// Replaces the embedded Input System action asset (InputActionAsset.FromJson("<json>")) in a game
// assembly: this port adds keyboard bindings to Navigate, because the Android player's game controller
// axes never reach the game, while its buttons do.
using Mono.Cecil;

if (args.Length < 3)
{
    Console.Error.WriteLine("usage: actionpatch <assembly.dll> <actions.json> <out dir>");
    return 2;
}
var managed = Path.GetDirectoryName(Path.GetFullPath(args[0]));
var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(managed);
var asm = AssemblyDefinition.ReadAssembly(args[0], new ReaderParameters { AssemblyResolver = resolver });

// C# literal form: the source used one line with \n and \" escapes; JSON's own escaping matches it
var json = File.ReadAllText(args[1]);
var literal = "\"" + json.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", "\\n") + "\"";

var hits = 0;
foreach (var type in asm.MainModule.Types.SelectMany(Types))
    foreach (var m in type.Methods.Where(m => m.HasBody))
        foreach (var ins in m.Body.Instructions)
            if (ins.OpCode.Code == Mono.Cecil.Cil.Code.Ldstr && ins.Operand is string s &&
                s.Contains("\"name\": \"LamentumControls\"") && s.Contains("\"maps\""))
            {
                ins.Operand = json.Replace("\r", "").Replace("\n", "\n");
                hits++;
            }

if (hits != 1)
{
    Console.Error.WriteLine($"expected exactly one action asset literal, found {hits}");
    return 1;
}
var outDir = Directory.CreateDirectory(args[2]).FullName;
var outFile = Path.Combine(outDir, Path.GetFileName(args[0]));
asm.Write(outFile);
Console.WriteLine($"patched {hits} action asset in {outFile} ({new FileInfo(outFile).Length} bytes)");
return 0;

static IEnumerable<TypeDefinition> Types(TypeDefinition t)
{
    yield return t;
    foreach (var n in t.NestedTypes.SelectMany(Types)) yield return n;
}
