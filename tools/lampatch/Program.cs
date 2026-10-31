// Lamentum: the resolution menu assumes Screen.resolutions is never empty; the Android player behind
// ua_host reports none, so ResolucionesCompatibles() returns an empty list and Start() dies on
// PosiblesResoluciones[Length - 1]. Fall back to the panel's own 1280x720 when the list is empty.
using Mono.Cecil;
using Mono.Cecil.Cil;

if (args.Length < 2)
{
    Console.Error.WriteLine("usage: lampatch <Assembly-CSharp.dll> <out dir>");
    return 2;
}
var managed = Path.GetDirectoryName(Path.GetFullPath(args[0]));
var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(managed);
var asm = AssemblyDefinition.ReadAssembly(args[0], new ReaderParameters { AssemblyResolver = resolver });

var type = asm.MainModule.Types.FirstOrDefault(t => t.Name == "ManagerMenuPrincipal")
           ?? throw new Exception("ManagerMenuPrincipal not found");
var m = type.Methods.FirstOrDefault(x => x.Name == "ResolucionesCompatibles")
        ?? throw new Exception("ResolucionesCompatibles not found");
var body = m.Body;
var il = body.GetILProcessor();

var resRef = asm.MainModule.GetTypeReferences().First(t => t.FullName == "UnityEngine.Resolution");
// IL2CPP needs field definitions, not bare field refs on a type ref: take them from the engine module.
var corePath = Path.Combine(managed, "UnityEngine.CoreModule.dll");
var core = AssemblyDefinition.ReadAssembly(corePath, new ReaderParameters { AssemblyResolver = resolver });
var resDef = core.MainModule.GetType("UnityEngine.Resolution")
             ?? throw new Exception("UnityEngine.Resolution not in CoreModule");
FieldReference F(string n) => asm.MainModule.ImportReference(resDef.Fields.First(f => f.Name == n));
var methods = body.Instructions.Select(i => i.Operand).OfType<MethodReference>().ToList();
var add = methods.First(r => r.Name == "Add" && r.DeclaringType.Name.StartsWith("List"));
var toArray = methods.Last(r => r.Name == "ToArray");
var listType = (GenericInstanceType)add.DeclaringType;
var getCount = new MethodReference("get_Count", asm.MainModule.TypeSystem.Int32, listType) { HasThis = true };
var listVar = body.Variables.First(v => v.VariableType.FullName == listType.FullName);
var resVar = new VariableDefinition(resRef);
body.Variables.Add(resVar);
m.Body.InitLocals = true;

var target = body.Instructions.Last(i => i.OpCode == OpCodes.Callvirt && i.Operand == toArray);
var skip = Instruction.Create(OpCodes.Nop);
foreach (var ins in new[]
{
    Instruction.Create(OpCodes.Ldloc, listVar),
    Instruction.Create(OpCodes.Callvirt, getCount),
    Instruction.Create(OpCodes.Brtrue, skip),
    Instruction.Create(OpCodes.Ldloca, resVar),
    Instruction.Create(OpCodes.Initobj, resRef),
    Instruction.Create(OpCodes.Ldloca, resVar),
    Instruction.Create(OpCodes.Ldc_I4, 1280),
    Instruction.Create(OpCodes.Stfld, F("m_Width")),
    Instruction.Create(OpCodes.Ldloca, resVar),
    Instruction.Create(OpCodes.Ldc_I4, 720),
    Instruction.Create(OpCodes.Stfld, F("m_Height")),
    Instruction.Create(OpCodes.Ldloca, resVar),
    Instruction.Create(OpCodes.Ldc_I4_S, (sbyte)60),
    Instruction.Create(OpCodes.Stfld, F("m_RefreshRate")),
    Instruction.Create(OpCodes.Ldloc, listVar),
    Instruction.Create(OpCodes.Ldloc, resVar),
    Instruction.Create(OpCodes.Callvirt, add),
    skip,
})
    il.InsertBefore(target, ins);

var outDir = Directory.CreateDirectory(args[1]).FullName;
var outFile = Path.Combine(outDir, "Assembly-CSharp.dll");
asm.Write(outFile);
Console.WriteLine($"patched {m.FullName} -> {outFile} ({new FileInfo(outFile).Length} bytes)");
return 0;
